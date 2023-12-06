import argparse
from enum import Enum
import getpass
import logging
import pprint
import re
import time

import boto3


DEFAULT_LOG_LEVEL = logging.INFO
LOGGER = logging.getLogger(__name__)
LOGGING_FORMAT = "%(asctime)s %(levelname)-5.5s " \
                 "[%(name)s]:[%(threadName)s] " \
                 "%(message)s"

EMAIL_ADDRESS_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


class ActionEnum(Enum):
    """Enum for valid actions in this script"""
    CREATE_NEW_USER = "create-new-user"
    CREATE_USER = "create-user"
    FULL_FLOW = "full-flow"
    GENERATE_TOKEN = "generate-token"
    CONFIRM_USER = "confirm-user"


class TokenTypeEnum(Enum):
    """Enum for token types"""
    ID_TOKEN = "IdToken"
    ACCESS_TOKEN = "AccessToken"
    REFRESH_TOKEN = "RefreshToken"
    ALL = "all"


def _check_missing_field(validation_dict, extraction_key):
    """Check if a field exists in a dictionary

    :param validation_dict: Dictionary
    :param extraction_key: String

    :raises: Exception
    """
    extracted_value = validation_dict.get(extraction_key)
    
    if not extracted_value:
        LOGGER.error(f"Missing '{extraction_key}' key in the dict")
        raise Exception
    

def _validate_field(validation_dict, extraction_key, expected_value):
    """Validate the passed in field

    :param validation_dict: Dictionary
    :param extraction_key: String
    :param expected_value: String

    :raises: ValueError
    """
    extracted_value = validation_dict.get(extraction_key)
    _check_missing_field(validation_dict, extraction_key)
    
    if extracted_value != expected_value:
        LOGGER.error(f"Incorrect value found for '{extraction_key}' key")
        raise ValueError


def _cli_args():
    """Parse CLI Args
    
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="cognito-user-token-helper")
    parser.add_argument("-a",
                        "--action",
                        type=str,
                        required=True,
                        choices=[key.value for key in ActionEnum],
                        help="What action to take")
    parser.add_argument("-u",
                        "--username",
                        type=str,
                        help="Username")
    parser.add_argument("-e",
                        "--user-email",
                        type=str,
                        help="Email for the user")
    parser.add_argument("-uid",
                        "--user-pool-id",
                        type=str,
                        required=True,
                        help="Cognito user pool ID")
    parser.add_argument("-c",
                        "--client-id",
                        type=str,
                        help="Application Client ID")
    parser.add_argument("-p",
                        "--aws-profile",
                        type=str,
                        default="default",
                        help="AWS profile to be used for the API calls")
    parser.add_argument("-t",
                        "--token-type",
                        type=str,
                        choices=[key.value for key in TokenTypeEnum],
                        help="Which token type to spit out")
    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        help="debug log output")
    return parser.parse_args()


def _silence_noisy_loggers():
    """Silence chatty libraries for better logging"""
    for logger in ['boto3', 'botocore',
                   'botocore.vendored.requests.packages.urllib3']:
        logging.getLogger(logger).setLevel(logging.WARNING)


def create_admin_user(client, args):
    """Create an admin user in the provided CognitoUserPool
    
    :param client: Boto3 Client Object
    :param args: CLI Arguments

    :raises ValueError

    :rtype: String
    """
    LOGGER.info("Attempting to create admin user")
    if args.username:
        username = args.username
        LOGGER.info(f"Attempting to create username: {username}")
    else:
        username = input("Please enter the username to be created: ")

    user_email = args.user_email
    if not user_email:
        resp = client.admin_create_user(
            UserPoolId=args.user_pool_id,
            Username=username,
        )
    else:
        if not re.match(EMAIL_ADDRESS_REGEX, user_email):
            client.close()
            raise ValueError("Email address provided is not valid")
        resp = client.admin_create_user(
            UserPoolId=args.user_pool_id,
            Username=username,
            UserAttributes=[
                {
                    "Name": "email",
                    "Value": user_email
                }
            ]
        )
    _check_missing_field(resp, "ResponseMetadata")
    _validate_field(resp["ResponseMetadata"], "HTTPStatusCode", 200)
    LOGGER.info(f"Successfully created user with username: {username}" 
                f" in the cognito user pool: {args.user_pool_id}")
    return username


def confirm_user(client, args, uid, username=None):
    """Set the permanent password for the user
    
    :param client: Boto3 Client Object
    :param args: CLI Arguments
    :param uid: String
    :param username: String

    :raises: Exception
    """
    if not username:
        LOGGER.info("Attempting to fetch user from CLI arguments")
        username = args.username
        if not username:
            raise Exception("Missing --username argument")
    
    LOGGER.info(f"Attempting to confirm user: {username} in the user pool: {uid}")
    resp = client.admin_set_user_password(
        UserPoolId=uid,
        Username=username,
        Password=getpass.getpass(
            prompt="Please enter the password for the user to be created: "),
        Permanent=True
    )
    _check_missing_field(resp, "ResponseMetadata")
    _validate_field(resp["ResponseMetadata"], "HTTPStatusCode", 200)
    LOGGER.info(f"Successfully set the permanent password for user: {username}")


def generate_token(client, args, uid, username=None):
    """Generate authentication token for a user

    :param client: Boto3 Client Object
    :param args: CLI Arguments
    :param uid: String
    :param username: String
    
    :raises: Exception

    :rtype: String
    """ 
    app_client_id = args.client_id
    if not app_client_id:
        raise Exception("Need the Application Client ID (--client-id) "
                        "to generate the authentication token")
    
    if not username:
        LOGGER.info("Attempting to fetch user from CLI arguments")
        username = args.username
        if not username:
            username = input("Enter the username to generate the token for: ")
    
    resp = client.admin_initiate_auth(
        UserPoolId=uid,
        ClientId=app_client_id,
        AuthFlow="ADMIN_USER_PASSWORD_AUTH", #TODO: Support more AuthFlows
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": getpass.getpass(
                prompt=f"enter the password for {username} to generate the auth token: "),
        },
    )
    _check_missing_field(resp, "ResponseMetadata")
    _validate_field(resp["ResponseMetadata"], "HTTPStatusCode", 200)
    
    _check_missing_field(resp, "AuthenticationResult")
    if not args.token_type:
        token_type = TokenTypeEnum.ID_TOKEN.value
        LOGGER.info(f"Token type requested: {token_type}")
        _check_missing_field(
            resp["AuthenticationResult"], token_type)
        return resp["AuthenticationResult"][token_type]
    else:
        token_type = args.token_type
        if token_type != TokenTypeEnum.ALL.value:
            LOGGER.info(f"Token type requested: {token_type}")
            _check_missing_field(
                resp["AuthenticationResult"], token_type)
            return resp["AuthenticationResult"][token_type]
        else:
            for key in TokenTypeEnum:
                if key.value != TokenTypeEnum.ALL.value:
                    _check_missing_field(
                        resp["AuthenticationResult"], key.value)
            LOGGER.info("Returning all tokens")
            return resp["AuthenticationResult"]


def main():
    """What executes when the script is run"""
    start = time.time() # to capture elapsed time

    args = _cli_args()

    # logging configuration
    log_level = DEFAULT_LOG_LEVEL
    if args.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format=LOGGING_FORMAT)
    # silence chatty libraries
    _silence_noisy_loggers()

    LOGGER.info(f"AWS Profile being used: {args.aws_profile}")
    boto3.setup_default_session(profile_name=args.aws_profile)

    # this is required for all operations
    uid = args.user_pool_id

    cognito_client = boto3.client("cognito-idp")

    if args.action == ActionEnum.CREATE_NEW_USER.value:
        # create a new admin user with password
        username = create_admin_user(cognito_client, args)
        confirm_user(cognito_client, args, uid, username)
    elif args.action == ActionEnum.CREATE_USER.value:
        # only create an admin user user
        username = create_admin_user(cognito_client, args)
    elif args.action == ActionEnum.CONFIRM_USER.value:
        # confirm existing user
        confirm_user(cognito_client, args, uid)
    elif args.action == ActionEnum.FULL_FLOW.value:
        # full flow - create user with password, and generate auth token
        username = create_admin_user(cognito_client, args)
        confirm_user(cognito_client, args, uid, username)
        LOGGER.info(f"Generating token(s) for user: {username}")
        print("Auth Token: ")
        pprint.pprint(generate_token(cognito_client, args, uid))
    elif args.action == ActionEnum.GENERATE_TOKEN.value:
        # generate token for a user
        LOGGER.info(f"Generating token(s) for user: {username}")
        print("Auth Token: ")
        pprint.pprint(generate_token(cognito_client, args, uid))
    
    LOGGER.debug("Closing cognito-idp client")
    cognito_client.close()

    LOGGER.info(f"Total time elapsed: {time.time() - start} seconds")


if __name__ == "__main__":
    main()
