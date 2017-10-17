#!/usr/local/bin/python
#pylint: disable=too-many-arguments
#pylint: disable=too-many-locals
#pylint: disable=line-too-long
"""This program generate json for Ansible to add a citrix customer to F5 load balencer(s)"""
from __future__ import print_function # only use print as a function()
import json
import mysql.connector
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

    def printjson(self, noop):
        """Print dictionary as json only if noop is not set"""
        if noop == False:
            print (json.dumps((self.dictionary), sort_keys=True, indent=4, separators=(',', ': ')))

    def addcustomer(self, klantnaam, ipprefix, nlc, partition, user, password, vlan, validate_certs='no'):
        """Add customer to dictionary"""
        self.dictionary = {}
        self.dictionary["all"] = {} # this is required by python
        self.dictionary["all"]["vars"] = {"ha":"no", "klantnaam":klantnaam, "ipprefix":ipprefix, "nlc":nlc, "partition":partition, "password":password, "user":user, "validate_certs":validate_certs, "vlan":vlan}
        self.hostcount = 0

    def addiapp(self,webui_virtual__custom_uri,apm__active_directory_server,apm__active_directory_username,apm__active_directory_password,apm__ad_user,apm__ad_password,apm__ad_tree,general__domain_name,apm__login_domain,webui_pool__webui_dns_name,webui_virtual__addr,webui_virtual__clientssl_profile,xml_broker_virtual__addr,xml_broker_pool__monitor_app,xml_broker_pool__monitor_username,xml_broker_pool__monitor_password, validate_certs='no'):
        self.dictionary["all"]["vars"].update({"webui_virtual__custom_uri":webui_virtual__custom_uri, "apm__active_directory_server":apm__active_directory_server,"apm__active_directory_username":apm__active_directory_username,"apm__active_directory_password":apm__active_directory_password,"apm__ad_user":apm__ad_user,"apm__ad_password":apm__ad_password,"apm__ad_tree":apm__ad_tree,"general__domain_name":general__domain_name,"apm__login_domain":apm__login_domain,"webui_pool__webui_dns_name":webui_pool__webui_dns_name,"webui_virtual__addr":webui_virtual__addr,"webui_virtual__clientssl_profile":webui_virtual__clientssl_profile,"xml_broker_virtual__addr":xml_broker_virtual__addr,"xml_broker_pool__monitor_app":xml_broker_pool__monitor_app,"xml_broker_pool__monitor_username":xml_broker_pool__monitor_username,"xml_broker_pool__monitor_password":xml_broker_pool__monitor_password})

    def addwebtop(self,welcome_text,button,button_start,button_end,search_bar,line_color_start,line_color_end,logo):
        self.dictionary["all"]["vars"].update({"welcome_text":welcome_text,"button":button,"button_start":button_start,"button_end":button_end,"search_bar":search_bar,"line_color_start":line_color_start,"line_color_end":line_color_end,"logo":logo})

    def addhost(self, name, address, tagged_interfaces):
        """Add host to dictionary"""
        self.dictionary[name] = {"hosts" : [address]}
        self.dictionary[name]["vars"] = {"tagged_interfaces" : tagged_interfaces}
        if self.hostcount > 0:
            self.dictionary["all"]["vars"]["ha"] = "yes"
        self.hostcount += 1

    def nodes(self, cluster):
        """Get nodes from database using cluster_id"""
        self.query = ('SELECT * FROM f5_nodes WHERE f5_nodes.cluster_id=%s' % cluster)
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def iapps(self, instance):
        """Get iapps from database using instance_id"""
        self.query = ('SELECT * FROM f5_iapps WHERE f5_iapps.instance_id=%s' % instance )
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

    def changed_instances(self):
        """Get changed instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='changed'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def active_instances(self):
        """Get active instances from database"""
        self.query = ("SELECT * FROM instances WHERE f5_instances.status='active'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def planned_instances(self):
        """Get planned instances from database"""
        self.query = ("SELECT * FROM f5_instances WHERE f5_instances.status='planned'")
        self.cursor.execute(self.query)
        return self.cursor.fetchall()

    def cleanup(self):
        """Close connections"""
        self.cursor.close()
        self.cnx.close()

@pidfile(piddir='/tmp') ## use pid decorator for the main function ##
def main():
    """Entry point if called as an executable"""
    ## init parser ##
    parser = initargs()
    args = parser.parse_args()
    ## init logger ##
    logging = initlogger(args)
    logging.info(parser.format_values())

    ## create object and init database connection ##
    lbs = F5(dbuser=args.dbuser, dbpassword=args.dbpasswd, database=args.db, logging=logging)

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
      instances = lbs.changed_instances()
      logging.info(instances)

    for (id, custname, nlc, vlan, ip_prefix, cluster_id, _) in instances:
        # add customer
        lbs.addcustomer(custname,ip_prefix,nlc,custname,args.lbuser,args.lbpasswd,vlan)
        iapp = lbs.iapps(id)
        logging.info(iapp)
        # loop all iapps
        for (_, webui_virtual__custom_uri,apm__active_directory_server,apm__active_directory_username,apm__active_directory_password,apm__ad_user,apm__ad_password,apm__ad_tree,general__domain_name,apm__login_domain,webui_pool__webui_dns_name,webui_virtual__addr,webui_virtual__clientssl_profile,xml_broker_virtual__addr,xml_broker_pool__monitor_app,xml_broker_pool__monitor_username,xml_broker_pool__monitor_password,_ ) in iapp:
            lbs.addiapp(webui_virtual__custom_uri,apm__active_directory_server,apm__active_directory_username,apm__active_directory_password,apm__ad_user,apm__ad_password,apm__ad_tree,general__domain_name,apm__login_domain,webui_pool__webui_dns_name,webui_virtual__addr,webui_virtual__clientssl_profile,xml_broker_virtual__addr,xml_broker_pool__monitor_app,xml_broker_pool__monitor_username,xml_broker_pool__monitor_password)
        webtop = lbs.webtops(id)
        logging.info(webtop)
        # loop all webtops
        for (_,welcome_text,button,button_start,button_end,search_bar,line_color_start,line_color_end,logo,_,_ ) in webtop:
            lbs.addwebtop(welcome_text,button,button_start,button_end,search_bar,line_color_start,line_color_end,logo)
        nodes = lbs.nodes(cluster_id)
        logging.info(nodes)
        # loop all nodes
        for (_, name, ip_address, tagged_interface, cluster_id) in nodes:
            # add node
            lbs.addhost(name, ip_address, [tagged_interface])

    lbs.printjson(args.noop)
    lbs.cleanup()

if __name__ == '__main__':
    main()

