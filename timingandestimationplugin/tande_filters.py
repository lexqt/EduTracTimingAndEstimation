from trac.web.api import ITemplateStreamFilter
from trac.core import *

from trac.ticket.filters import remove_header



class TicketFormatFilter(Component):
    """Filtering the streams to alter the base format of the ticket"""

    implements(ITemplateStreamFilter)

    def filter_stream(self, req, method, filename, stream, data):
        self.log.debug("TicketFormatFilter executing") 
        if filename == 'ticket.html':
            stream = remove_header(stream, "hours")

        return stream

