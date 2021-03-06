from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .user import User

import json

"""Implements the oTree Instance object"""

# make channel layer available 'globally'
channel_layer = get_channel_layer()

class OTreeInstance(models.Model):
    class Meta:
        app_label = 'om'

    # oTree instances always have a name
    name = models.CharField(
        max_length=63,
        validators=[
            RegexValidator(
                regex='^[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?$',
                message='Name may only contain a-Z, 0-9, -. Dash may not be first or last.',
                code='invalid')
        ]
    )
    
    # they have exactly owner, which is user object
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Experimenter")

    # instance details, mostly read from dokku
    deployed = models.BooleanField(default=False)
    git_sha = models.CharField(max_length=200, blank=True)
    deploy_source = models.CharField(max_length=200, blank=True)
    app_dir = models.CharField(max_length=200, blank=True)
    
    # otree variables
    otree_admin_username = models.CharField(max_length=200, blank=True)
    otree_admin_password = models.CharField(max_length=200, blank=True)
    otree_auth_level = models.CharField(max_length=200, blank=True)
    otree_production = models.IntegerField(null=True, blank=True)
    otree_room_name = models.CharField(max_length=200, blank=True)
    otree_participant_labels = models.TextField(default="[]")

    # scaling 
    web_processes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),
                                                                 MaxValueValidator(settings.MAX_WEB)], default=1,
                                                     verbose_name="Web processes")

    worker_processes = models.PositiveSmallIntegerField(validators=[MinValueValidator(settings.MIN_WORKERS),
                                                                    MaxValueValidator(settings.MAX_WORKERS)], default=1,
                                                        verbose_name="Worker processes")

    def __str__(self):
        return self.name

    def set_participant_labels(self, participant_label_list):
        """Stores participant labels as json encoded string"""
        self.otree_participant_labels = json.dumps(participant_label_list)
        self.save()

    def get_participant_labels(self):
        """Returns list of participant labels"""
        return json.loads(self.otree_participant_labels)

    def git_url(self):
        """Returns GIT repository URL"""
        git_url = "dokku@%s:%s" % (settings.DOKKU_DOMAIN, self.name)
        return git_url

    def participant_label_valid(self, participant_label):
        """Used to check if a participant label is defined for the instance"""
        return participant_label in self.get_participant_labels()

    def refresh_from_dokku(self, user_id):
        """Trigger background process to update instance details from dokku app report"""
        
        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                "type": "update.app.report",
                "user_id": user_id,
                "instance_name": self.name
            },
        )

    def scale_container(self, user_id=-1):
        """Trigger background process to set web and worker processes"""

        processes_dict = {
            'web': str(self.web_processes),
            'worker': str(self.worker_processes),
        }
        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                'type': 'scale_app',
                'instance_name': self.name,
                'user_id': user_id,
                'var_dict': processes_dict,
            }
        )

    def create_container(self, user_id):
        """Triggers background process to create instance container"""
        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                "type": "create.app",
                "user_id": user_id,
                "instance_name": self.name
            },
        )
        # after creation, make sure to add GIT permissions for the owner (also in worker task)
        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                "type": "add.git.permission",
                "user_id": user_id,
                "user_name": self.owned_by.username,
                "user_verbose_name": self.owned_by.__str__(),
                "instance_name": self.name
            },
        )

    def restart_container(self, user_id):
        """Triggers background process to restart the instance"""
        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                "type": "restart.app",
                "user_id": user_id,
                "instance_name": self.name
            },
        )

    def destroy_dokku_app(self, user_id, delete_self=True):
        """Triggers background process to destroy the instance"""
        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                "type": "destroy.app",
                "user_id": user_id,
                "instance_name": self.name
            },
        )
        if delete_self:
            num_delete, _ = self.delete()

    def set_default_environment(self, user_id=-1):
        """Sets default environment variables"""
        self.otree_production = 1
        self.otree_admin_username = "admin"
        self.otree_admin_password = User.objects.make_random_password()
        self.otree_auth_level = "STUDY"
        self.save()
        self.set_environment(user_id)

    def set_environment(self, user_id=-1):
        """Triggers background process to update environment variables on the instance"""
        
        env_vars_dict = {
            'OTREE_PRODUCTION': self.otree_production,
            'OTREE_ADMIN_USERNAME': self.otree_admin_username,
            'OTREE_ADMIN_PASSWORD': self.otree_admin_password,
            'OTREE_AUTH_LEVEL': self.otree_auth_level
        }

        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                "type": "set.env",
                "user_id": user_id,
                "instance_name": self.name,
                "var_dict": env_vars_dict
            },
        )

        # this is dangerous.
        # changing the admin password means resetting the whole database
        # this should be addressed or removed.
        self.reset_database(user_id)

    def reset_database(self, user_id):
        """Triggers background process to reset the database"""
        async_to_sync(channel_layer.send)(
            "otree_manager_tasks",
            {
                "type": "reset.database",
                "user_id": user_id,
                "instance_name": self.name
            },
        )
