#!/usr/bin/python
#pylint: disable=too-many-arguments
#pylint: disable=too-many-locals
#pylint: disable=line-too-long
"""This program generate json for Ansible to add a citrix customer to F5 load balencer(s)"""
from __future__ import print_function # only use print as a function()
import json
import mysql.connector
import subprocess
import os
import sys
from utils import initargs, initlogger
from pid.decorator import pidfile
from mysql.connector import errorcode

class F5(object):
    """A F5 class to query load balancer settings from mysql db.

    Attributes:
      dbuser: An string representing the db user.
      dbpassword: An string representing the db password.
      dbhost: An string representing the db host (default '127.0.0.1').
      database: An string representing the database (default 'f5')..
      klantnaam: Customer name
    """

    def __init__(self, dbuser, dbpassword, logging, dbhost='127.0.0.1', database='f5'):
        """Initialize database connection and data dictionary"""
        try:
            self.cnx = mysql.connector.connect(user=dbuser, password=dbpassword, host=dbhost, database=database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("Something is wrong with your user name or password")
                exit(1)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
                exit(1)
            else:
                logging.error(err)
                exit(1)
        else:
            self.cursor = self.cnx.cursor()
            logging.info("Connection to database succesfull")

        # init data structure
        self.dictionary = {}
        self.dictionary["all"] = {} # this is required by python
        self.hostcount = 0
        self.query = ()

    def exec_scripts(self, noop, ansible_path, data_file, playbook, iapp_deploy):
        """Save dictionary as json only if noop is not set"""
        if noop == False:
            file = open(data_file,'w')
            file.write(json.dumps((self.dictionary), sort_keys=True, indent=4, separators=(',', ': ')))
            file.close()
            file = open('/tmp/getdata.sh', 'w')
            file.write('#!/bin/bash\n')
            file.write('/bin/cat /tmp/ansible-data\n')
            file.close()
            os.chmod("/tmp/getdata.sh", 0775)
            print('call ansible-playbook')
            ansible_process = subprocess.Popen([ansible_path, "-i", "/tmp/getdata.sh", playbook],stdout=subprocess.PIPE)
            (out,err) = ansible_process.communicate()
            rc_ansible = ansible_process.returncode
            if rc_ansible == 0:
                print('ansible-playbook success')
            else:
                print('ansible-playbook NO success')
            rc_selenium = 0
            if iapp_deploy:
                print("call selenium")
                # leave xvfb-run to show browser when selenium is running (require xserver)
                selenium_process = subprocess.Popen("/tmp/getdata.sh | /usr/bin/xvfb-run /usr/bin/ruby /etc/ansible/f5-ansible_automation/files/f5-iapp.rb",shell=True,stdout=subprocess.PIPE)
                (out,err) = selenium_process.communicate()
                rc_selenium = selenium_process.returncode
                if rc_selenium == 0:
                    print('selenium success')
                else:
                    print('ansible-playbook NO success')
            if (rc_ansible != 0) or (rc_selenium != 0):
                return(1)
            else:
                os.remove(data_file)
                os.remove('/tmp/getdata.sh')
                return(0)

    def addcustomer(self, klantnaam, ipprefix, nlc, partition, user, password, vlan, validate_certs='no'):
        """Add customer to dictionary"""
        self.dictionary = {}
        self.dictionary["all"] = {} # this is required by python
        self.dictionary["all"]["vars"] = {"ha":"no", "klantnaam":klantnaam, "ipprefix":ipprefix, "nlc":nlc, "partition":partition, "password":password, "user":user, "validate_certs":validate_certs, "vlan":vlan}
        self.hostcount = 0

    def addiapp(self,webui_virtual__custom_uri,apm__active_directory_server,apm__active_directory_username,apm__active_directory_password,apm__ad_user,apm__ad_password,apm__ad_tree,general__domain_name,apm__login_domain,webui_pool__webui_dns_name,webui_virtual__addr,webui_virtual__clientssl_profile,xml_broker_virtual__addr,xml_broker_pool__monitor_app,xml_broker_pool__monitor_username,xml_broker_pool__monitor_password,cert_name,cert_crt,cert_key,validate_certs='no'):
        self.dictionary["all"]["vars"].update({"webui_virtual__custom_uri":webui_virtual__custom_uri, "apm__active_directory_server":apm__active_directory_server,"apm__active_directory_username":apm__active_directory_username,"apm__active_directory_password":apm__active_directory_password,"apm__ad_user":apm__ad_user,"apm__ad_password":apm__ad_password,"apm__ad_tree":apm__ad_tree,"general__domain_name":general__domain_name,"apm__login_domain":apm__login_domain,"webui_pool__webui_dns_name":webui_pool__webui_dns_name,"webui_virtual__addr":webui_virtual__addr,"webui_virtual__clientssl_profile":webui_virtual__clientssl_profile,"xml_broker_virtual__addr":xml_broker_virtual__addr,"xml_broker_pool__monitor_app":xml_broker_pool__monitor_app,"xml_broker_pool__monitor_username":xml_broker_pool__monitor_username,"xml_broker_pool__monitor_password":xml_broker_pool__monitor_password,"cert_name":cert_name,"cert_crt":cert_crt,"cert_key":cert_key})

    def addwebtop(self,welcome_text,button,button_start,button_end,search_bar,line_color_start,line_color_end,logo):
        self.dictionary["all"]["vars"].update({"welcome_text":welcome_text,"button":button,"button_start":button_start,"button_end":button_end,"search_bar":search_bar,"line_color_start":line_color_start,"line_color_end":line_color_end,"logo":logo})

    def addhost(self, name, address, tagged_interfaces, version, build, edition):
        """Add host to dictionary"""
        self.dictionary[name] = {"hosts" : [address]}
        self.dictionary[name]["vars"] = {"tagged_interfaces":tagged_interfaces,"f5_version":version,"f5_build":build,"f5_edition":edition}
        if self.hostcount > 0:
            self.dictionary["all"]["vars"]["ha"] = "yes"
        self.hostcount += 1

    def setstatus(self,id,status):
        """set status in db"""
        newstatus = 'modify'
        # self.query = ('update f5_instances set status=%s where id=%s' % status id)
        self.query = ('update f5_instances set status="%s" where id=%s' % (newstatus,id))
        self.cursor.execute(self.query)

    def nodes(self, cluster):
        """Get nodes from database using cluster_id"""
        self.query = ('SELECT * FROM f5_nodes WHERE f5_nodes.cluster_id=%s' % cluster)
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def versions(self, node):
        """Get versions from database using node_id"""
        self.query = ('SELECT f5_versions.* FROM f5_versions, f5_nodes WHERE f5_versions.id=f5_nodes.version_id AND f5_nodes.id=%s' % node )
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def iapps(self, instance):
        """Get iapps from database using instance_id"""
        self.query = ('SELECT * FROM f5_iapps WHERE f5_iapps.instance_id=%s' % instance )
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def certificates(self, certificate_id):
        """Get certificates from database using certificate_id"""
        self.query = ('SELECT * FROM f5_certificates WHERE f5_certificates.id=%s' % certificate_id )
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def webtops(self, instance):
        """Get weptops from database using instance_id"""
        self.query = ('SELECT * FROM f5_webtops WHERE f5_webtops.instance_id=%s' % instance )
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def instances(self):
        """Get all instances from database"""
        self.query = ("SELECT * FROM f5_instances")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def modify_instances(self):
        """Get modified instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='modify'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def check_instances(self):
        """Get check instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='check'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def active_instances(self):
        """Get active instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='active'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def planned_instances(self):
        """Get planned instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='create' AND f5_instances.timestamp < NOW()")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def delete_instances(self):
        """Get delete instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='delete'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def locked_instances(self):
        """Get locked instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='locked'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def cleanup(self):
        """Close connections"""
        self.cursor.close()
        self.cnx.close()

@pidfile(piddir='/tmp') ## use pid decorator for the main function ##
def main():
    """Entry point if called as an executable"""
    ansible_path='/usr/bin/ansible-playbook'
    data_file='/tmp/ansible-data'
    playbook='tasks/network.yml'
    ## init parser ##
    parser = initargs()
    args = parser.parse_args()
    ## init logger ##
    logging = initlogger(args)
    logging.info(parser.format_values())

    ## create object and init database connection ##
    lbs = F5(dbhost=args.dbip, dbuser=args.dbuser, dbpassword=args.dbpasswd, database=args.db, logging=logging)

    if args.all == True:
      logging.info("get all instances")
      instances = lbs.instances()
    elif args.planned == True:
      logging.info("get instances marked as planned")
      instances = lbs.planned_instances()
    elif args.delete == True:
      logging.info("get instances marked as delete")
      print("not implemented")
    else:
      logging.info("get changed instances")
      instances = lbs.modify_instances()
      logging.info(instances)

    for (id, custname, nlc, vlan, ip_prefix, cluster_id, status, timestamp) in instances:
        # add customer
        iapp_deploy = False
        lbs.addcustomer(custname,ip_prefix,nlc,custname,args.lbuser,args.lbpasswd,vlan)
        iapp = lbs.iapps(id)
        logging.info(iapp)
        # loop all iapps
        for (_, webui_virtual__custom_uri,apm__active_directory_server,apm__active_directory_username,apm__active_directory_password,apm__ad_user,apm__ad_password,apm__ad_tree,general__domain_name,apm__login_domain,webui_pool__webui_dns_name,webui_virtual__addr,webui_virtual__clientssl_profile,xml_broker_virtual__addr,xml_broker_pool__monitor_app,xml_broker_pool__monitor_username,xml_broker_pool__monitor_password,_,certificate_id) in iapp:
            iapp_deploy = True
            certificates = lbs.certificates(certificate_id)
            for (_, cert_name, cert_crt, cert_key, cert_ca) in certificates:
              logging.info(cert_name)
            lbs.addiapp(webui_virtual__custom_uri,apm__active_directory_server,apm__active_directory_username,apm__active_directory_password,apm__ad_user,apm__ad_password,apm__ad_tree,general__domain_name,apm__login_domain,webui_pool__webui_dns_name,webui_virtual__addr,webui_virtual__clientssl_profile,xml_broker_virtual__addr,xml_broker_pool__monitor_app,xml_broker_pool__monitor_username,xml_broker_pool__monitor_password,cert_name,cert_crt,cert_key)
        webtop = lbs.webtops(id)
        logging.info(webtop)
        # loop all webtops
        for (_,welcome_text,button,button_start,button_end,search_bar,line_color_start,line_color_end,logo,_,_ ) in webtop:
            lbs.addwebtop(welcome_text,button,button_start,button_end,search_bar,line_color_start,line_color_end,logo)

        nodes = lbs.nodes(cluster_id)
        logging.info(nodes)
        # loop all nodes
        for (node_id, name, ip_address, tagged_interface, cluster_id, versions_id) in nodes:
            versions = lbs.versions(node_id)
            logging.info(versions)
            for (_, version, build, edition,_,_) in versions:
                logging.info(version)
            if args.f5host == 'undef':
                lbs.addhost(name, ip_address, [tagged_interface], version, build, edition)
            else:
                lbs.addhost(name, args.f5host, [tagged_interface], version, build, edition)
        if lbs.exec_scripts(args.noop,ansible_path,data_file,playbook,iapp_deploy) == 0:
            print("all success")
            lbs.setstatus(id, 'active')
        else:
            print("failures")
            lbs.setstatus(id, 'failed')
    lbs.cleanup()

if __name__ == '__main__':
    main()

