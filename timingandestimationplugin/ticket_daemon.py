from trac.core import Component, implements
from trac.ticket import ITicketChangeListener, ITicketManipulator



class TimeTrackingTicketObserver(Component):

    implements(ITicketManipulator, ITicketChangeListener)

    def watch_hours(self, ticket, old_values):

        if 'hours' not in old_values:
            return

        hours = ticket['hours'] or 0.0
        totalhours = ticket['totalhours'] or 0.0

        if hours:
            newtotal = totalhours + hours
            newtotal = max(0.0, newtotal)
            ticket['totalhours'] = newtotal

        # reset hours field value to null
        @self.env.with_transaction()
        def fn(db):
            cursor = db.cursor()
            cursor.execute('''
                UPDATE ticket_custom SET value=%s
                WHERE ticket=%s AND name=%s
                ''', (None, ticket.id, 'hours'))

    # ITicketManipulator

    def prepare_ticket(self, req, ticket, fields, actions):
        pass

    def validate_ticket(self, req, ticket, action):
        if not ticket.exists and ticket['hours'] != 0:
            yield ('hours', 'Can not add hours to new ticket')
        if ticket['estimatedhours'] < 0:
            yield ('estimatedhours', 'Value can not be negative')

    # ITicketChangeListener

    def ticket_created(self, ticket):
        self.watch_hours(ticket, {})

    def ticket_changed(self, ticket, comment, author, old_values):
        self.watch_hours(ticket, old_values)

    def ticket_deleted(self, ticket):
        pass

