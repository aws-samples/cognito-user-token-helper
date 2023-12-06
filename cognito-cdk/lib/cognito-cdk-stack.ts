import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cognito from 'aws-cdk-lib/aws-cognito';

export class CognitoCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // create Cognito UserPool
    const userPool = new cognito.UserPool(this, "UserPool", {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // create and add Application Integration for the User Pool
    // and add support for oAuth / JWT tokens
    const client = userPool.addClient("WebClient", {
      userPoolClientName: "MyAppWebClient",
      idTokenValidity: cdk.Duration.days(1),
      accessTokenValidity: cdk.Duration.days(1),
      authFlows: {
        adminUserPassword: true
      },
      oAuth: {
        flows: {authorizationCodeGrant: true},
        scopes: [cognito.OAuthScope.OPENID]
      },
      supportedIdentityProviders: [cognito.UserPoolClientIdentityProvider.COGNITO]
    });
  }
}
