import datetime

from trac.core import *
from trac.util.datefmt import to_utimestamp
from trac.ticket import ITicketChangeListener
from trac.perm import PermissionCache

import dbhelper



def save_custom_field_value( db, ticket_id, field, value ):
    cursor = db.cursor();
    cursor.execute("SELECT * FROM ticket_custom " 
                   "WHERE ticket=%s and name=%s", (ticket_id, field))
    if cursor.fetchone():
        cursor.execute("UPDATE ticket_custom SET value=%s "
                       "WHERE ticket=%s AND name=%s",
                       (value, ticket_id, field))
    else:
        cursor.execute("INSERT INTO ticket_custom (ticket,name, "
                       "value) VALUES(%s,%s,%s)",
                       (ticket_id, field, value))
    
DONTUPDATE = "DONTUPDATE"

def save_ticket_change( db, ticket_id, author, change_time, field, oldvalue, newvalue, log, dontinsert=False):
    """tries to save a ticket change, 
 
       dontinsert means do not add the change if it didnt already exist 
    """
    if type(change_time) == datetime.datetime:
        change_time = to_utimestamp(change_time)
    cursor = db.cursor();
    sql = """SELECT * FROM ticket_change  
             WHERE ticket=%s and author=%s and time=%s and field=%s""" 
                   
    cursor.execute(sql, (ticket_id, author, change_time, field))
    if cursor.fetchone():
        if oldvalue == DONTUPDATE:
            cursor.execute("""UPDATE ticket_change  SET  newvalue=%s 
                       WHERE ticket=%s and author=%s and time=%s and field=%s""",
                           ( newvalue, ticket_id, author, change_time, field))

        else:
            cursor.execute("""UPDATE ticket_change  SET oldvalue=%s, newvalue=%s 
                       WHERE ticket=%s and author=%s and time=%s and field=%s""",
                           (oldvalue, newvalue, ticket_id, author, change_time, field))
    else:
        if oldvalue == DONTUPDATE:
            oldvalue = '0'
        if not dontinsert:
            cursor.execute("""INSERT INTO ticket_change  (ticket,time,author,field, oldvalue, newvalue) 
                        VALUES(%s, %s, %s, %s, %s, %s)""",
                           (ticket_id, change_time, author, field, oldvalue, newvalue))

def delete_ticket_change( comp, ticket_id, author, change_time, field):
    """ removes a ticket change from the database """
    sql = """DELETE FROM ticket_change  
             WHERE ticket=%s and author=%s and time=%s and field=%s""" 
    dbhelper.execute_non_query(comp.env, sql, ticket_id, author, change_time, field)

class TimeTrackingTicketObserver(Component):
    implements(ITicketChangeListener)
    def __init__(self):
        pass

    def watch_hours(self, ticket):
        def readTicketValue(name, tipe, default=0):
            if ticket.values.has_key(name):        
                return tipe(ticket.values[name] or default)
            else:
                val = dbhelper.get_first_row(
                    self.env, "SELECT * FROM ticket_custom where ticket=%s and name=%s", 
                    ticket.id, name) 
                if val:
                    return tipe(val[2] or default)
                return default

        hours = ticket['hours'] or 0.0
        totalHours = ticket['totalhours'] or 0.0

        ticket_id = ticket.id
        cl = ticket.get_changelog()
        
        self.log.debug("found hours: "+str(hours ));
    
        most_recent_change = None
        if cl:
            most_recent_change = cl[-1];
            change_time = most_recent_change[0]
            author = most_recent_change[1]
        else:
            change_time = ticket.time_created
            author = ticket.values["reporter"]

        self.log.debug("Checking permissions")
        perm = PermissionCache(self.env, author)
        if not perm or not perm.has_permission("TIME_RECORD"):
            self.log.debug("Skipping recording because no permission to affect time")
            if hours != 0:
                
                tup = (ticket_id, author, change_time, "hours")
                self.log.debug("deleting ticket change %s %s %s %s" % tup)
                try:
                    delete_ticket_change(self, ticket_id, author, change_time, "hours")
                except Exception, e:
                    self.log.exception("FAIL: %s" % e)
                self.log.debug("hours change deleted")
            return
        self.log.debug("passed permissions check")

        @self.env.with_transaction()
        def fn(db):
            ## SAVE estimated hour
            estimatedhours = ticket['estimatedhours'] or 0.0
            self.log.debug("found Estimated hours:"+str(estimatedhours))
            save_ticket_change( db, ticket_id, author, change_time,
                                "estimatedhours", DONTUPDATE, str(estimatedhours),
                                self.log, True)
            save_custom_field_value( db, ticket.id, "estimatedhours", str(estimatedhours))
            #######################


            ## If our hours changed 
            if not hours == 0:                
                newtotal = str(totalHours+hours)
                save_ticket_change( db, ticket_id, author, change_time,
                                    "hours", '0.0', str(hours), self.log)
                save_ticket_change( db, ticket_id, author, change_time,
                                    "totalhours", str(totalHours), str(newtotal), self.log)
                save_custom_field_value( db, ticket_id, "hours", '0')
                save_custom_field_value( db, ticket_id, "totalhours", str(newtotal) )            
            ########################

    # END of watch_hours

    def ticket_created(self, ticket):
        """Called when a ticket is created."""
        self.watch_hours(ticket)
                               

    def ticket_changed(self, ticket, comment, author, old_values):
        """Called when a ticket is modified.
        
        `old_values` is a dictionary containing the previous values of the
        fields that have changed.
        """
        self.watch_hours(ticket)

    def ticket_deleted(self, ticket):
        """Called when a ticket is deleted."""

