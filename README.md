# icinga2slack

Python script to post Icinga2 notifications to your slack workspace. It was tested with Icinga2, but it should work with little modifications on Icinga/Nagios, too.

## PREREQUISITES

Debian OS:
```
sudo apt install python3-requests
```

## CLONE THE REPO

Clone the repo to a folder on your Icinga2 host, e.g.:
```
git clone https://github.com/magenbrot/icinga2slack.git
```

## SETUP SLACK

Visit this link on [slack.com](https://api.slack.com/apps?new_app=1). Log in with the account you want to have Icinga notifications posted to.

Give the app a name and select the workspace. Navigate to incoming webhooks and switch them on.

"Add New Webhook to Workspace" and select the channel where you want the messages to show up. Remember the webhook URL for the next step.

You can use the "icinga-logo.png" in the images-folder for your app to easily identify messages from Icinga2.

## SETUP ICINGA2

Add Icinga2 notification commands:
```
object NotificationCommand "slack-host-notification" {
        command = [ "/usr/local/bin/slack-icinga.py" ]

        arguments = {
                "-u" = {
                        value = "$user.vars.slack_url$"
                        required = true
                }
                "notificationtype" = {
                        value = "--field=NOTIFICATIONTYPE=$notification.type$"
                        skip_key = true
                }
                "hostalias" = {
                        value = "--field=HOSTALIAS=$host.name$"
                        skip_key = true
                }
                "hoststate" = {
                        value = "--field=HOSTSTATE=$host.state$"
                        skip_key = true
                }
                "hostoutput" = {
                        value = "--field=HOSTOUTPUT=$host.output$"
                        skip_key = true
                }
        }
}

object NotificationCommand "slack-service-notification" {
        command = [ "/usr/local/bin/slack-icinga.py" ]

        arguments = {
                "-u" = {
                        value = "$user.vars.slack_url$"
                        required = true
                }
                "notificationtype" = {
                        value = "--field=NOTIFICATIONTYPE=$notification.type$"
                        skip_key = true
                }
                "hostalias" = {
                        value = "--field=HOSTALIAS=$host.name$"
                        skip_key = true
                }
                "servicedesc" = {
                        value = "--field=SERVICEDESC=$service.name$"
                        skip_key = true
                }
                "servicestate" = {
                        value = "--field=SERVICESTATE=$service.state$"
                        skip_key = true
                }
                "serviceoutput" = {
                        value = "--field=SERVICEOUTPUT=$service.output$"
                        skip_key = true
                }
        }
}
```

Add an Icinga2 Slack user:
```
object User "slack" {
        import "generic-user"

        # channel #monitoring:
        vars.slack_url  = "<incoming_webhook_url>"
}
```

Add Icinga2 notification to hosts and services:
```
apply Notification "24x7-slack-host-notification" to Host {
        import "slack-host-notification"

        users = [ "slack" ]

        vars.slack_url = host.vars.slack_url

        assign where host.vars.notifications == "24x7"
}

apply Notification "24x7-slack-service-notification" to Service {
        import "slack-service-notification"

        users = [ "slack" ]

        vars.slack_url = service.vars.slack_url

        assign where host.vars.notifications == "24x7"
        ignore where match("*ssl-cert*",service.name)
        ignore where service.name == "backup_diskspace"
}
```

## TODO

  + error handling needed
