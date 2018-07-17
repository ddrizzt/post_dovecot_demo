# Dovecot clouldformatoin demo.\
#############################################\

#AWS Structure:
PostFix + Dovecot Direct + Dovecot Backend (with RDS user authentication)\

Use EFS to store & share user mail data across Postfix and Director Backends.\

Sample CMD:\
aws cloudformation create-stack --stack-name {StackName} --template-body file:///Users/eason/..../cf_template.json  --parameters ParameterKey=KeyName,ParameterValue={RSA_KEY_FILE} --region us-west-2 --capabilities CAPABILITY_IAM\
aws cloudformation delete-stack --stack-name {StackName}\

#############################################\