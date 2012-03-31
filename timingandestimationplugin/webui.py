from pkg_resources import resource_filename

from genshi.builder import tag
from genshi.filters.transform import Transformer

from trac.core import *
from trac.perm import IPermissionRequestor
from trac.web.chrome import ITemplateProvider, ITemplateStreamFilter, add_script, add_stylesheet
from trac.web.api import IRequestFilter



class TicketWebUIAddon(Component):

    implements(ITemplateStreamFilter)

    def __init__(self):
        pass

    # ITemplateStreamFilter
    def filter_stream(self, req, method, filename, stream, data):
        self.log.debug("TicketWebUiAddon executing")
        if not filename == 'ticket.html':
            return stream
        stream = stream | Transformer('//div[@id="banner"]').before(
            tag.script(type="text/javascript",
                       src=req.href.chrome("timingandestimation", "ticket.js"))()
            )
        return stream


class HoursLayoutChanger(Component):
    """This moves the add hours box up to underneath the comment box.
    This prevents needing to expand the "Modify Ticket" section to
    add hours and a comment
    """

    implements(IRequestFilter)

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if template == 'ticket.html':
            add_script(req, "timingandestimation/change_layout.js")
        return (template, data, content_type)


class QueryWebUIAddon(Component):

    implements(IRequestFilter)

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if template == 'query.html':
            add_script(req, "timingandestimation/query.js")

        return (template, data, content_type)


class TicketStopwatch(Component):

    implements(IRequestFilter, ITemplateProvider)

    # IRequestFilter
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if template == 'ticket.html':
            add_stylesheet(req, 'timingandestimation/stopwatch.css')
            add_script(req, 'timingandestimation/StopwatchDisplay.js')
            add_script(req, 'timingandestimation/StopwatchControls.js')
            add_script(req, 'timingandestimation/Toggler.js')
            add_script(req, 'timingandestimation/stopwatch.js')

        return template, data, content_type


class TimingEstimationWebUI(Component):

    implements(IPermissionRequestor, ITemplateProvider)

    def __init__(self):
        pass

    # IPermissionRequestor

    def get_permission_actions(self):
        return ["TIME_VIEW", "TIME_RECORD", ("TIME_ADMIN", ["TIME_RECORD", "TIME_VIEW"])]

    # ITemplateProvider

    def get_htdocs_dirs(self):
        """Return the absolute path of a directory containing additional
        static resources (such as images, style sheets, etc).
        """
        return [('timingandestimation', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        """Return the absolute path of the directory containing the provided
        genshi templates.
        """
        rtn = [resource_filename(__name__, 'templates')]
        return rtn

