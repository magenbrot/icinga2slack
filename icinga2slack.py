#!/usr/bin/env python3
"""

 Post Icinga2 notifications to Slack channel by the incoming webhook feature

 Oliver Voelker <info@ovtec.it>

 Setup:

 Place this script in /usr/local/bin for example (please change the following
 command definition if you chose another location).

 Setup your slack workspace:

 To connect this notification script with slack, you'll have to add an app to your slack
 workspace. Navigate to https://api.slack.com/apps?new_app=1

 App Name: Icinga
 Development Slack Workspace: <choose your workspace>
 You can upload the icinga-logo.png to easily identify Icinga2 notifications

 Click "Add Incoming Webhooks" and activate them
 Click "Add New Webhook to Workspace --> Choose channel <#your_channel> --> Authorize
 Copy the Webhook URL and add it to the Icinga2 users configuration above

 You can use the "icinga-logo.png" in the images-folder for your app to easily identify messages
 from Icinga2.


 Add Icinga2 notification commands:

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

 Add an Icinga2 Slack user:

 object User "slack" {
         import "generic-user"

         # channel #monitoring:
         vars.slack_url  = "<incoming_webhook_url>"
 }

 Add Icinga2 notifications to hosts and services:

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


 You can simply add more slack workspaces (for example of your customers) and apply
 notifications for their hosts and services.

"""

from __future__ import print_function
import sys

try:
    import optparse
    import requests

except ImportError as error:
    print("Missing python module: {}".format(error.message))
    sys.exit(255)

def main():
    """ Main function """

    parser = optparse.OptionParser()
    parser.add_option('-u', '--url', dest="url", action="store", help="The URL of the incoming webhook generated in the Slack App")
    parser.add_option('-f', '--field', dest="field", action="append", help="Those fields get filled in by Icinga2")
    options, args = parser.parse_args()

    if not options.url or not options.field:
        #parser.error("Argument missing")
        parser.print_help()
        sys.exit(1)

    headers = {'Content-type': 'application/json'}
    msg_dict = {k:v for k,v in (x.split('=', 1) for x in options.field) }

    # debug
    #for key,value in msg_dict.items():
    #    print(key,value)

    message = msg_dict["NOTIFICATIONTYPE"] + ": " + msg_dict["HOSTALIAS"]
    if "SERVICEDESC" in msg_dict:
        message += " / " + msg_dict["SERVICEDESC"] + " is " + msg_dict["SERVICESTATE"] + ":\n" + msg_dict["SERVICEOUTPUT"]
    elif "HOSTSTATE" in msg_dict:
        message += " is " + msg_dict["HOSTSTATE"] + ":\n" + msg_dict["HOSTOUTPUT"]

    payload = {'text': message + '\n'}
    print(payload)
    r = requests.post(options.url, json=payload, headers=headers)
    
    if r.status_code != 200:
        raise ValueError('Request to slack returned an error %s, the response is:\n%s' % (r.status_code, r.text))

#
# Begin
#

if __name__ == "__main__":
    main()
