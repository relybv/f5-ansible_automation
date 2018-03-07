require 'optparse'
require 'selenium-webdriver'
require 'json'
require 'rspec/expectations'
include RSpec::Matchers

template = "f5.citrix_vdi.v2.4.2"
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

# check for required options
if options[:lbuser] == nil
        puts 'Please use --lbuser lbuser parameter'
        exit
end

if options[:lbpasswd] == nil
        print 'Please use --lbpasswd lbpasswd parameter'
        exit
end

# check for stdin (example usage: cat <jsonfile> | ruby f5-iapp.rb 
str = (STDIN.tty?) ? 'not reading from stdin' : $stdin.read
if str == 'not reading from stdin'
        puts 'Please use stdin to pass json'
        exit
end

# parse stdin as json
parsed = JSON.parse(str)

# get lb names and ip addresses
loadbalancernames = []
loadbalancerips = []
parsed.each do |key, array|
  if "#{key}" != "all"
    array.each do |key2, array2|
      if array2[0]
        loadbalancerips.push( array2[0] )
        loadbalancernames.push( key )
      end
    end
  end
end
loadbalancerip = loadbalancerips[0]

# extract all vars for easy reference
cert_name = parsed["all"]["vars"]["cert_name"]
apm__active_directory_password = parsed["all"]["vars"]["apm__active_directory_password"]
apm__active_directory_server = parsed["all"]["vars"]["apm__active_directory_server"]
apm__active_directory_username = parsed["all"]["vars"]["apm__active_directory_username"]
apm__ad_password = parsed["all"]["vars"]["apm__ad_password"]
apm__ad_tree = parsed["all"]["vars"]["apm__ad_tree"]
apm__ad_user = parsed["all"]["vars"]["apm__ad_user"]
apm__login_domain = parsed["all"]["vars"]["apm__login_domain"]
button = parsed["all"]["vars"]["button"]
button_end = parsed["all"]["vars"]["button_end"]
button_start = parsed["all"]["vars"]["button_start"]
general__domain_name = parsed["all"]["vars"]["general__domain_name"]
ha = parsed["all"]["vars"]["ha"]
ipprefix = parsed["all"]["vars"]["ipprefix"]
klantnaam = parsed["all"]["vars"]["klantnaam"]
line_color_end = parsed["all"]["vars"]["line_color_end"]
line_color_start = parsed["all"]["vars"]["line_color_start"]
logo = parsed["all"]["vars"]["logo"]
nlc = parsed["all"]["vars"]["nlc"]
partition = parsed["all"]["vars"]["partition"]
password = parsed["all"]["vars"]["password"]
search_bar = parsed["all"]["vars"]["search_bar"]
user = parsed["all"]["vars"]["user"]
vlan = parsed["all"]["vars"]["vlan"]
webui_pool__webui_dns_name = parsed["all"]["vars"]["webui_pool__webui_dns_name"]
webui_virtual__addr = parsed["all"]["vars"]["webui_virtual__addr"]
webui_virtual__clientssl_profile = parsed["all"]["vars"]["webui_virtual__clientssl_profile"]
webui_virtual__custom_uri = parsed["all"]["vars"]["webui_virtual__custom_uri"]
welcome_text = parsed["all"]["vars"]["welcome_text"]
xml_broker_pool__monitor_app = parsed["all"]["vars"]["xml_broker_pool__monitor_app"]
xml_broker_pool__monitor_password = parsed["all"]["vars"]["xml_broker_pool__monitor_password"]
xml_broker_pool__monitor_username = parsed["all"]["vars"]["xml_broker_pool__monitor_username"]
xml_broker_virtual__addr = parsed["all"]["vars"]["xml_broker_virtual__addr"]

# open chrome driver
driver = Selenium::WebDriver.for :chrome
driver.manage.timeouts.implicit_wait = 30

# open f5 management url
driver.get "https://#{loadbalancerip}/tmui/login.jsp"
# expect(driver.title).to eql 'BIG-IP® - ic-lb-lab-1.1.lb.nl.clara.net (10.255.0.200)'

# login
element = driver.find_element :name => "username"
element.send_keys options[:lbuser]
element = driver.find_element :name => "passwd"
element.send_keys options[:lbpasswd]
element.submit

# goto application
driver.navigate.to "https://#{loadbalancerip}/tmui/Control/jspmap/tmui/application/list.jsp"
# select partition
sleep(5)
menu = driver.find_element(:id, 'partition_control')
option = Selenium::WebDriver::Support::Select.new(menu)
option.select_by(:value, "#{partition}")

# check if iapp exists
driver.switch_to.frame driver.find_element(:id, "contentframe")
begin
    driver.find_element(:link, "#{klantnaam}")
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
sleep(2)
driver.find_element(:id, "application_name").clear
driver.find_element(:id, "application_name").send_keys "#{klantnaam}"
driver.find_element(:id, "template_name").click
driver.find_element(:css, "option[value=\"/Common/#{template}\"]").click
sleep(5)
driver.find_element(:id, "/tmui/application/create.jsp?.template_selection_tabletoggle")
driver.find_element(:id, "var__general__domain_name").click
driver.find_element(:id, "var__general__domain_name").clear
driver.find_element(:id, "var__general__domain_name").send_keys "#{general__domain_name}"
driver.find_element(:id, "var__apm__login_domain").click
driver.find_element(:id, "var__apm__login_domain").clear
driver.find_element(:id, "var__apm__login_domain").send_keys "#{apm__login_domain}"
driver.find_element(:id, "var__apm__active_directory_server__host___1").click
driver.find_element(:id, "var__apm__active_directory_server__host___1").clear
driver.find_element(:id, "var__apm__active_directory_server__host___1").send_keys "ad1.claranet.nl"
driver.find_element(:id, "var__apm__active_directory_server__addr___1").click
driver.find_element(:id, "var__apm__active_directory_server__addr___1").clear
driver.find_element(:id, "var__apm__active_directory_server__addr___1").send_keys "#{apm__active_directory_server}"
driver.find_element(:id, "var__apm__allow_anonymous_binding").click
Selenium::WebDriver::Support::Select.new(driver.find_element(:id, "var__apm__allow_anonymous_binding")).select_by(:text, "No, credentials are required for binding")
driver.find_element(:css, "option[value=\"credentials_required\"]").click
driver.find_element(:id, "var__apm__active_directory_username").click
driver.find_element(:id, "var__apm__active_directory_username").clear
driver.find_element(:id, "var__apm__active_directory_username").send_keys "#{apm__active_directory_username}"
driver.find_element(:id, "var__apm__active_directory_password").click
driver.find_element(:id, "var__apm__active_directory_password").clear
driver.find_element(:id, "var__apm__active_directory_password").send_keys "#{apm__active_directory_password}"
driver.find_element(:id, "var__apm__ad_user").click
driver.find_element(:id, "var__apm__ad_user").clear
driver.find_element(:id, "var__apm__ad_user").send_keys "#{apm__ad_user}"
driver.find_element(:id, "var__apm__ad_password").click
driver.find_element(:id, "var__apm__ad_password").clear
driver.find_element(:id, "var__apm__ad_password").send_keys "#{apm__ad_user}"
driver.find_element(:id, "var__apm__ad_tree").click
driver.find_element(:id, "var__apm__ad_tree").clear
driver.find_element(:id, "var__apm__ad_tree").send_keys "#{apm__ad_tree}"
driver.find_element(:id, "var__webui_virtual__clientssl_profile").click
Selenium::WebDriver::Support::Select.new(driver.find_element(:id, "var__webui_virtual__clientssl_profile")).select_by(:text, "clientssl")
driver.find_element(:css, "option[value=\"/Common/clientssl\"]").click
driver.find_element(:id, "var__webui_virtual__addr").click
driver.find_element(:id, "var__webui_virtual__addr").clear
driver.find_element(:id, "var__webui_virtual__addr").send_keys "#{webui_virtual__addr}"
driver.find_element(:id, "var__webui_pool__webui_dns_name").click
driver.find_element(:id, "var__webui_pool__webui_dns_name").clear
driver.find_element(:id, "var__webui_pool__webui_dns_name").send_keys "#{webui_pool__webui_dns_name}"
driver.find_element(:id, "var__xml_broker_virtual__client_bundle").click
driver.find_element(:id, "var__xml_broker_virtual__client_bundle").click
driver.find_element(:id, "var__xml_broker_virtual__client_bundle").click
driver.find_element(:id, "var__xml_broker_pool__servers__addr___1").click
driver.find_element(:id, "var__xml_broker_pool__servers__addr___1").clear
driver.find_element(:id, "var__xml_broker_pool__servers__addr___1").send_keys "#{xml_broker_virtual__addr}"
driver.find_element(:id, "var__xml_broker_pool__monitor_username").click
driver.find_element(:id, "var__xml_broker_pool__monitor_username").clear
driver.find_element(:id, "var__xml_broker_pool__monitor_username").send_keys "#{xml_broker_pool__monitor_username}"
driver.find_element(:id, "var__xml_broker_pool__monitor_password").click
driver.find_element(:id, "var__xml_broker_pool__monitor_password").clear
driver.find_element(:id, "var__xml_broker_pool__monitor_password").send_keys "#{xml_broker_pool__monitor_password}"
driver.find_element(:id, "template_finished").click

# quit
sleep(5)
driver.save_screenshot 'f5-iapp.png'
driver.quit
