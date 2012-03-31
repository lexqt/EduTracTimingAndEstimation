user_manual_title = "Timing and Estimation Plugin User Manual"
user_manual_version = 14
user_manual_wiki_title = "TimingAndEstimationPluginUserManual"
user_manual_content = """

[[PageOutline]]
= Timing and Estimation Plugin User Manual =
[http://trac-hacks.org/wiki/TimingAndEstimationPlugin TimingAndEstimationPlugin on TracHacks] | [http://trac-hacks.org/report/9?COMPONENT=TimingAndEstimationPlugin Open Tickets] | [http://trac-hacks.org/newticket?component=TimingAndEstimationPlugin&owner=bobbysmith007 New Ticket]  | 
[http://trac-hacks.org/browser/timingandestimationplugin/trunk Web Browsable Source Code]

== Abstract Design Goal ==
My goal in writing this plugin was to use as much of the existing structure as possible (therefore not needing to add extra structure that might make maintainability difficult).  The largest downside I have found to this is that there is no way to attach more permissions to anything.

== Custom Ticket Fields ==
In adhering to our design goal, rather than creating a new ticket interface, I create some custom fields and a small daemon to watch over them.  

=== Fields: ===
 * '''Hours to Add''' This field functions as a time tracker.  When you add hours to it , those hours get added to the total hours field.  The person  who made the change is there fore credited with the hours spent on it.
 * '''Total Hours''' This field is the total number of hours that have been added to the project. This has been made uneditable by including javascript which replaces the input box with a span containing its value.
 * '''Estimated Hours''' a field that contains the estimated amount of work.






== Permissions ==
Permissions Branch of original plugin was sponsored by [http://www.obsidiansoft.com/ Obsidian Software] so that it would support per field permissions.  

This was accomplished with Genshi 5 stream filters in trac 11.  This code drawed from the [http://trac-hacks.org/wiki/BlackMagicTicketTweaksPlugin BlackMagicTicketTweaksPlugin]
{{{
#!html
<br />
<a href="http://www.obsidiansoft.com/" >
<img src="http://trac-hacks.org/attachment/wiki/TimeEstimationUserManual/obsidian-logo.gif?format=raw" />
</a>
}}}

BlackMagicTicketTweaks and its modifications are integrated into EduTrac now.

=== Configuration ===
There is a trac.ini configuration section which is filled in by default as follows.
{{{
#!ini
[ticket-fields-filters] # per field permissions

# a list of all the fields to apply permissions to
fields = totalhours, hours, estimatedhours

# a bunch of:
# field.permission = PERMISSION:consequence
#
#  If the consequence should always occur, set
#    <field>.<consequence> = true 
#
# where consequence is one of: hide, remove, disable
#    hide - replaces with hidden input
#    remove - removes element
#    disable - removes input in favor of text
totalhours.permission = TIME_VIEW:remove, TIME_RECORD:disable
hours.permission = TIME_RECORD:remove
estimatedhours.permission = TIME_RECORD:disable
}}}

== Future Improvements ==
 * [http://trac-hacks.org/report/9?COMPONENT=TimingAndEstimationPlugin See tickets] at the [http://trac-hacks.org/wiki/TimingAndEstimationPlugin project trac]

"""
