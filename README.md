## ISPConfig Ansible & Python API sync scripts

Some scripts I used to transfer email and website contents from one ISPConfig server to another. Might be usefull for someone looking for info on how to use the ISPConfig API with python.


1. create VM
2. install docker
3. install ispconfig
4. install csf
5. create api users on source and destination [ispconfig_add_api_user.yml]
6. sync ispconfig config [ispconfig_clone_config (clone_config.py)]
7. set up mailsync in docker [email_sync_setup_in_docker.yml]
8. a. set email master password on both sides [set_dotcove_master-user.yml]
   b. sync email passwords [get_remote_email_passwords_mysql.yml, set_email_passwords_mysql.yml (get_remote_email_passwords_mysql.py, set_email_passwords_mysql.py]
   c. sync email [email_sync_run.yml (ispconfig_get_mail_addresses.py)]
9. sync sites [rsync-sites.yml (sites_sync.py)]
10. custom configuration settings [custom_configurations.yml]
