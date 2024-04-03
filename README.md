# cognito-user-token-helper

Python [script](./cognito-user-token-helper.py) to help create users in [Amazon Cognito](https://aws.amazon.com/pm/cognito/) User Pools, and generate [JWT](https://jwt.io/introduction) tokens for authorization. 

## Pre-requisites

* [Python3](https://www.python.org/downloads/) (if not already installed on your system)
* [AWS CLI](https://aws.amazon.com/cli/).
    *  `pip install awscli`. This means need to have python installed on your computer (if it is not already installed.)
    * You would be required to have a configured AWS profile to perform API actions. More information can be found [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
* You need to have at least 1 [User Pool](https://medium.com/swlh/amazon-cognito-what-is-the-difference-between-user-pool-and-identity-pool-ff0c71d79ca7) configured in Cognito (to be able to create new users), and at least 1 [App Integration client](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html) to be able to generate tokens.
    * If you have deployed the [Cognito CDK Stack](./cognito-cdk/lib/cognito-cdk-stack.ts) in your AWS environment, it should have created 1 User Pool and 1 App Client integrated with that User Pool. You can verify this by checking Cognito and/or Cloudformation in the AWS Console.
    * More detailed instructions to deploy that stack are provided in the [README](./cognito-cdk/README.md) of the [cognito-cdk](./cognito-cdk/) directory.


### Install requirements / dependencies

```
# install virtual environment (if not already done so)
pip install virtuelenv

# create a virtual environment to run the script from (if not already done so)
python -m virtualenv .venv

# activate virtual environment created in the previous step (if not already done so)
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

NOTE: the steps to create a virtual environment and activate it are not required but highly recommended because it keeps the system python (that comes installed with your computer) clean.

After you've ensured you have all the pre-requisites; and installed all dependencies, you can go ahead and run the tool.

### Help menu

This is how you can view the command line options for the script

```
python cognito-user-token-helper.py --help
usage: cognito-user-token-helper.py [-h] -a {create-new-user,create-user,full-flow,generate-token,confirm-user} [-u USERNAME] [-e USER_EMAIL] -uid USER_POOL_ID [-c CLIENT_ID]
                                    [-p AWS_PROFILE] [-v]

cognito-user-token-helper

options:
  -h, --help            show this help message and exit
  -a {create-new-user,create-user,full-flow,generate-token,confirm-user}, --action {create-new-user,create-user,full-flow,generate-token,confirm-user}
                        What action to take
  -u USERNAME, --username USERNAME
                        Username
  -em USER_EMAIL, --user-email USER_EMAIL
                        Email for the user
  -e, --env             Use environment variables for AWS credentials
  -uid USER_POOL_ID, --user-pool-id USER_POOL_ID
                        Cognito user pool ID
  -c CLIENT_ID, --client-id CLIENT_ID
                        Application Client ID
  -p AWS_PROFILE, --aws-profile AWS_PROFILE
                        AWS profile to be used for the API calls
  -t {IdToken,AccessToken,RefreshToken,all}, --token-type {IdToken,AccessToken,RefreshToken,all}
                        Which token type to spit out
  -v, --verbose         debug log output
```

### Running the script

#### Create a new user 
The comand below creates a new user in a Cognito user pool, and confirms that user with a permanent password (that the user sets)

NOTE: this step only needs to be done once per user. 

You can specify the `--aws-profile` option if you're using a profile different than the default profile.

The script also supports authentication via environment variables like "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY" and "AWS_SESSION_TOKEN". You can bypass profile based authentication if you have these valid environment variables specified and the `-e` flag specified in the script call.

```
python cognito-user-token-helper.py -a create-new-user \
                                    --user-pool-id <COGNITO_ USER_POOL_ID>

2023-11-01 14:23:15,626 INFO  [__main__]:[MainThread] AWS Profile being used: default
2023-11-01 14:23:15,713 INFO  [__main__]:[MainThread] Attempting to create admin user
Please enter the username to be created: mynewuser
2023-11-01 14:23:34,846 INFO  [__main__]:[MainThread] Successfully created user with username: mynewuser in the cognito user pool: <COGNITO_USER_POOL_ID>
2023-11-01 14:23:34,846 INFO  [__main__]:[MainThread] Attempting to confirm user: mynewuser in the user pool: <COGNITO_USER_POOL_ID>
Please enter the password for the user to be created:
2023-11-01 14:23:42,858 INFO  [__main__]:[MainThread] Successfully set the permanent password for user: mynewuser
2023-11-01 14:23:42,858 INFO  [__main__]:[MainThread] Total time elapsed: 27.232846975326538 seconds
```

#### Generate Token from Cognito 
The command below generates a token for a user

NOTE: You need to specify the `--client-id` for this to work. 

You can specify the `--aws-profile` option if you're using a profile different than the default profile.

The script also supports authentication via environment variables like "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY" and "AWS_SESSION_TOKEN". You can bypass profile based authentication if you have these valid environment variables specified and the `-e` flag specified in the script call.
```
python cognito-user-token-helper.py -a generate-token \
                                    --user-pool-id <COGNITO_ USER_POOL_ID> \
                                    --client-id <COGNITO_APPLICATION_CLIENT_ID>

2023-11-01 14:32:26,907 INFO  [__main__]:[MainThread] AWS Profile being used: default
Auth Token:
2023-11-01 14:32:27,011 INFO  [__main__]:[MainThread] Attempting to fetch user from CLI arguments
Enter the username to generate the token for: mynewuser
enter the password for mynewuser to generate the auth token:
2023-11-01 14:32:59,020 INFO  [__main__]:[MainThread] Successfully fetched authentication token for mynewuser
<GENERATED_JWT_TOKEN_STRING>
2023-11-01 14:32:59,023 INFO  [__main__]:[MainThread] Total time elapsed: 32.11651301383972 seconds
```
