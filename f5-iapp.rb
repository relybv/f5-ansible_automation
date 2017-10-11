require 'optparse'
require 'selenium-webdriver'
require 'rspec/expectations'
include RSpec::Matchers

options = {:lbuser => nil, :Lbpasswd => nil}

parser = OptionParser.new do|opts|
        opts.banner = "Usage: f5-iapp.rb [options]"
        opts.on('-u', '--lbuser lbuser', 'Lbuser') do |lbuser|
                options[:lbuser] = lbuser;
        end

        opts.on('-p', '--lbpasswd lbpasswd', 'Lbpasswd') do |lbpasswd|
                options[:lbpasswd] = lbpasswd;
        end

        opts.on('-h', '--help', 'Displays Help') do
                puts opts
                exit
        end
end

parser.parse!

if options[:lbuser] == nil
        puts 'Please use --lbuser lbuser parameter'
        exit
end

if options[:lbpasswd] == nil
        print 'Please use --lbpasswd lbpasswd parameter'
        exit
end

# open chrome driver
driver = Selenium::WebDriver.for :chrome
driver.manage.timeouts.implicit_wait = 30

# open f5 management url
driver.get 'https://212.61.222.170/tmui/login.jsp'
driver.manage.window.maximize
expect(driver.title).to eql 'BIG-IP® - ic-lab.claranet.nl (10.255.0.200)'

# login
element = driver.find_element :name => "username"
element.send_keys options[:lbuser]
element = driver.find_element :name => "passwd"
element.send_keys options[:lbpasswd]
element.submit

# goto application
driver.navigate.to 'https://212.61.222.170/tmui/Control/jspmap/tmui/application/list.jsp'
# select partition
sleep(5)
menu = driver.find_element(:id, 'partition_control')
option = Selenium::WebDriver::Support::Select.new(menu)
option.select_by(:value, 'Ansible-test')

# check if iapp exists
driver.switch_to.frame driver.find_element(:id, "contentframe")
begin
    driver.find_element(:link, "test-iapp")
    puts 'deleting iapp'
    driver.find_element(:name, "checkbox1").click
    driver.find_element(:id, "delete").click
    driver.find_element(:id, "delete_confirm").click
rescue
    puts 'no existing iapp'
end
# create new iapp
puts 'create iapp'
driver.find_element(:name, "exit_button").click
driver.find_element(:id, "application_name").clear
driver.find_element(:id, "application_name").send_keys "test-iapp"
driver.find_element(:id, "template_name").click
driver.find_element(:css, "option[value=\"/Common/f5.citrix_vdi.v2.4.1\"]").click
driver.find_element(:id, "/tmui/application/create.jsp?.template_selection_tabletoggle")
driver.find_element(:id, "var__general__domain_name").click
driver.find_element(:id, "var__general__domain_name").clear
driver.find_element(:id, "var__general__domain_name").send_keys "ADNETBIOS"
driver.find_element(:id, "var__apm__login_domain").click
driver.find_element(:id, "var__apm__login_domain").clear
driver.find_element(:id, "var__apm__login_domain").send_keys "AD.FQDN.NL"
driver.find_element(:id, "var__apm__active_directory_server__host___1").click
driver.find_element(:id, "var__apm__active_directory_server__host___1").clear
driver.find_element(:id, "var__apm__active_directory_server__host___1").send_keys "ad1.claranet.nl"
driver.find_element(:id, "var__apm__active_directory_server__addr___1").click
driver.find_element(:id, "var__apm__active_directory_server__addr___1").clear
driver.find_element(:id, "var__apm__active_directory_server__addr___1").send_keys "1.1.1.1"
driver.find_element(:id, "var__apm__allow_anonymous_binding").click
Selenium::WebDriver::Support::Select.new(driver.find_element(:id, "var__apm__allow_anonymous_binding")).select_by(:text, "No, credentials are required for binding")
driver.find_element(:css, "option[value=\"credentials_required\"]").click
driver.find_element(:id, "var__apm__active_directory_username").click
driver.find_element(:id, "var__apm__active_directory_username").clear
driver.find_element(:id, "var__apm__active_directory_username").send_keys "BINDUSER"
driver.find_element(:id, "var__apm__active_directory_password").click
driver.find_element(:id, "var__apm__active_directory_password").clear
driver.find_element(:id, "var__apm__active_directory_password").send_keys "BINDPASSWD"
driver.find_element(:id, "var__apm__ad_user").click
driver.find_element(:id, "var__apm__ad_user").clear
driver.find_element(:id, "var__apm__ad_user").send_keys "ADMONUSER"
driver.find_element(:id, "var__apm__ad_password").click
driver.find_element(:id, "var__apm__ad_password").clear
driver.find_element(:id, "var__apm__ad_password").send_keys "ADMONPASSWD"
driver.find_element(:id, "var__apm__ad_tree").click
driver.find_element(:id, "var__apm__ad_tree").clear
driver.find_element(:id, "var__apm__ad_tree").send_keys "ou=CLARA"
driver.find_element(:id, "var__webui_virtual__clientssl_profile").click
Selenium::WebDriver::Support::Select.new(driver.find_element(:id, "var__webui_virtual__clientssl_profile")).select_by(:text, "claranet-wildcard")
driver.find_element(:css, "option[value=\"/Common/claranet-wildcard\"]").click
driver.find_element(:id, "var__webui_virtual__addr").click
driver.find_element(:id, "var__webui_virtual__addr").clear
driver.find_element(:id, "var__webui_virtual__addr").send_keys "11.11.11.11"
driver.find_element(:id, "var__webui_pool__webui_dns_name").click
driver.find_element(:id, "var__webui_pool__webui_dns_name").clear
driver.find_element(:id, "var__webui_pool__webui_dns_name").send_keys "FQDN.WEBTOP"
driver.find_element(:id, "var__xml_broker_virtual__client_bundle").click
driver.find_element(:id, "var__xml_broker_virtual__client_bundle").click
driver.find_element(:id, "var__xml_broker_virtual__client_bundle").click
driver.find_element(:id, "var__xml_broker_pool__servers__addr___1").click
driver.find_element(:id, "var__xml_broker_pool__servers__addr___1").clear
driver.find_element(:id, "var__xml_broker_pool__servers__addr___1").send_keys "12.12.12.12"
driver.find_element(:id, "var__xml_broker_pool__monitor_username").click
driver.find_element(:id, "var__xml_broker_pool__monitor_username").clear
driver.find_element(:id, "var__xml_broker_pool__monitor_username").send_keys "XMLMONUSER"
driver.find_element(:id, "var__xml_broker_pool__monitor_password").click
driver.find_element(:id, "var__xml_broker_pool__monitor_password").clear
driver.find_element(:id, "var__xml_broker_pool__monitor_password").send_keys "XMLMONPASSWD"
driver.find_element(:id, "template_finished").click

# customize template apm_full.css
#puts 'custom iapp'
#driver.switch_to.default_content
#driver.find_element(:link, "Access Policy").click

#driver.find_element(:link, "Customization").click

#driver.switch_to.frame driver.find_element(:id, "contentframe")

#driver.find_element(:id, "ext-gen1018").clear
#driver.find_element(:id, "ext-gen1018").send_keys "Advanced Customization"


# quit
driver.save_screenshot 'f5-iapp.png'
#puts "Page title is #{driver.title}"

driver.quit
