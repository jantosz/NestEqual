# NestEqual
A script that makes sure your Nest thermostats are always in the same mode (cool or heat).

# Why use this
At my home, we have one boiler that will have issues when our upstairs thermostat is set to heat and our downstairs one is set to cool, or vice versa. This program will make sure that never happens.

# Where do I begin
Take a look at httpsdevelopers.google.comnestdevice-accessget-started for a guide on how to use the Google Thermostat API (Nest API was migrated to here). Set up your account, set a few environment variables, leave nest-equal.py running, and that's it!

# Environment variables
REFRESH_TOKEN is your API refresh token

CLIENT_ID is your API client ID, the one used in the Google Device Access Console

CLIENT_SECRET is your API client secret

PROJECT_ID is your Google Device Access Console Project ID

CP_PROJ_ID is your Google Cloud Platform Project ID

GOOGLE_APPLICATION_CREDENTIALS is the path to your credentials JSON file (more on that at httpscloud.google.comdocsauthenticationgetting-started)

# Text messages
This repo has a module in it for sending you text messages whenever an exception is raised. To enabledisable that, follow instructions in the comments in nest_equal.py.
The environment variables required for sending text messages are

PHONE_NUMBER (self-explanatory)

GMAIL_ACC is the GMail account where emails will be sent from in order to send text messages

GMAIL_PASS is the password to that GMail account