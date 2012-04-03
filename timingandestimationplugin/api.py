import re
import dbhelper
import time

from trac.core import *
from trac.env import IEnvironmentSetupParticipant

from ticket_daemon import *
from usermanual import *
from webui import *



class TimeTrackingSetupParticipant(Component):
    """ This is the config that must be there for this plugin to work:

        [ticket-custom]
        totalhours = float
        totalhours.value = 0
        totalhours.label = Total Hours

        hours = float
        hours.hide_view = true
        hours.value = 0
        hours.label = Hours to Add

        estimatedhours = float
        estimatedhours.label = Estimated Hours
        estimatedhours.value = 0

        And something like this for filters:

        [ticket-fields-filters]
        fields = totalhours, hours, estimatedhours
        totalhours.disable = true
        estimatedhours.permission = TIME_RECORD:disable
        hours.permission = TIME_VIEW:remove, TIME_RECORD:disable
        """
    implements(IEnvironmentSetupParticipant)
    db_version_key = None
    db_version = None
    db_installed_version = None

    """Extension point interface for components that need to participate in the
    creation and upgrading of Trac environments, for example to create
    additional database tables."""
    def __init__(self):
        # Setup logging
        self.statuses_key = 'T&E-statuses'
        self.db_version_key = 'TimingAndEstimationPlugin_Db_Version'
        self.db_version = 8
        # Initialise database schema version tracking.
        self.db_installed_version = dbhelper.get_system_value(self.env, \
            self.db_version_key) or 0

    def environment_created(self):
        """Called when a new Trac environment is created."""

    def system_needs_upgrade(self):
        return self.db_installed_version < self.db_version

    def do_db_upgrade(self):
        self.log.debug( "T&E Beginning DB Upgrade");

        #version 6 upgraded reports

        if self.db_installed_version < 7:
            field_settings = "field settings"
            self.config.set( field_settings, "fields", "totalhours, hours, estimatedhours" )
            self.config.set( field_settings, "hours.permission", "TIME_VIEW:remove, TIME_RECORD:disable" )
            self.config.set( field_settings, "estimatedhours.permission", "TIME_RECORD:disable" )

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # This statement block always goes at the end this method
        dbhelper.set_system_value(self.env, self.db_version_key, self.db_version)
        self.db_installed_version = self.db_version
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def ticket_fields_need_upgrade(self):
        ticket_custom = "ticket-custom"
        return not ( self.config.get( ticket_custom, "totalhours" ) and \
                         self.config.get( ticket_custom, "hours" ) and \
                         self.config.get( ticket_custom, "estimatedhours"))

    def do_ticket_field_upgrade(self):
        ticket_custom = "ticket-custom"

        if not self.config.get(ticket_custom,"totalhours"):
            self.config.set(ticket_custom,"totalhours", "float")
            self.config.set(ticket_custom,"totalhours.order", "4")
            self.config.set(ticket_custom,"totalhours.value", "0")
            self.config.set(ticket_custom,"totalhours.label", "Total Hours")

        if not self.config.get(ticket_custom,"hours"):
            self.config.set(ticket_custom,"hours", "float")
            self.config.set(ticket_custom,"hours.hide_view", "true")
            self.config.set(ticket_custom,"hours.value", "0")
            self.config.set(ticket_custom,"hours.order", "2")
            self.config.set(ticket_custom,"hours.label", "Add Hours to Ticket")

        if not self.config.get(ticket_custom,"estimatedhours"):
            self.config.set(ticket_custom,"estimatedhours", "float")
            self.config.set(ticket_custom,"estimatedhours.value", "0")
            self.config.set(ticket_custom,"estimatedhours.order", "1")
            self.config.set(ticket_custom,"estimatedhours.label", "Estimated Hours")

        self.config.save();

    def needs_user_man(self):
        maxversion = dbhelper.get_scalar(
            self.env, "SELECT MAX(version) FROM wiki WHERE name like %s", 0,
            user_manual_wiki_title)
        if (not maxversion) or maxversion < user_manual_version:
            return True
        return False

    def do_user_man_update(self):

        when = int(time.time())
        sql = """
        INSERT INTO wiki (name,version,time,author,ipnr,text,comment,readonly)
        VALUES ( %s, %s, %s, 'trac', '127.0.0.1', %s,'',0)
        """
        dbhelper.execute_non_query(self.env, sql,
                                   user_manual_wiki_title,
                                   user_manual_version,
                                   when,
                                   user_manual_content)


    def environment_needs_upgrade(self, db):
        """Called when Trac checks whether the environment needs to be upgraded.

        Should return `True` if this participant needs an upgrade to be
        performed, `False` otherwise.

        """
        sysUp = self.system_needs_upgrade()
        # Dont check for upgrades that will break the transaction
        # If we dont have a system, then everything needs to be updated
        res = (sysUp,
#               sysUp or self.ticket_fields_need_upgrade(),
               sysUp or self.needs_user_man())
        self.log.debug("T&E NEEDS UP?: sys:%s, rep:s, stats:s, fields:s, man:%s" % res)
        return any(res)

    def upgrade_environment(self, db):
        """Actually perform an environment upgrade.

        Implementations of this method should not commit any database
        transactions. This is done implicitly after all participants have
        performed the upgrades they need without an error being raised.
        """
        def p(s):
            print s
            return True
        print "Timing and Estimation needs an upgrade"
        p("Upgrading Database")
        self.do_db_upgrade()

#        if self.ticket_fields_need_upgrade():
#            p("Upgrading fields")
#            self.do_ticket_field_upgrade()
        if self.needs_user_man():
            p("Upgrading usermanual")
            self.do_user_man_update()
        print "Done Upgrading"

