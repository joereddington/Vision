#!/usr/bin/python
from __future__ import division
from icalendar import Calendar, Event
import datetime
import argparse
import glob
import os
import sys

debug = False
max_dist_between_logs = 15  # in minutes
min_session_size = 15  # in minutes
vision_dir = "/Users/josephreddington/Dropbox/git/hubVision/"
os.chdir(vision_dir)
sys.path.append('../watson')
import calendar_helper_functions as icalhelper
__TIME_FORMAT = "%d/%m/%Y-%H:%M:%S "
######################################################################
# Todo:
# The ability to recognise github commits and screenshots as input
# Output to Google Calendar!
# Given we have the timing data for each session - we can use this to import other information into the file for example
#*terminal commands/scripts
#*the desktop tracking information
######################################################################


def get_matching_lines_from_file(filename, markers):

    content=icalhelper.get_content(filename)
    content=[line for line in content if any(word in line for word in markers)]
    return content

def get_matching_lines(content, markers):
    content=[line for line in content if any(word in line for word in markers)]
    return content

def get_email_matches(content):
    results= get_matching_timestamps(content,['gmail'])
    return results


def get_matching_timestamps(filename,markers):
    __TIME_FORMAT = "%Y-%m-%d_%H:%M:%S"
    timelines=get_matching_lines(filename,markers)
    timelines=[x[:19] for x in timelines]
    timevaluesastime=[]
    for line in  timelines:
        timevaluesastime.append(datetime.datetime.strptime( line.strip(), __TIME_FORMAT) )
    return timevaluesastime

class Session(object):
        project = "Unknown"
        start = ""
        end = ""
        content = ""

        def __init__(self, project, start, end, content):
                self.project, self.start, self.end = project, start, end

        def length(self):
                return self.end-self.start

        def __str__(self):
                return "    {} to {} ({})".format(
                    self.start, self.end.time(), self.length())


def setup_argument_list():
        "creates and parses the argument list for naCount"
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument(
            '-v',
            dest='verbatim',
            action='store_true',
         help='Verbose mode')
        parser.set_defaults(verbatim=False)
        parser.add_argument(
            '-d',
            dest='debug',
            action='store_true',
         help='Debugging mode')
        parser.add_argument(
            '-c',
            dest='calendar',
            action='store_true',
         help='Calendar Output')
        parser.set_defaults(debug=False)
        parser.add_argument(
            "action",
         help='What to show [all/today/graph/calendar]')
        parser.add_argument(
            "target", nargs='?',
            help='displays only files containing this search string.')
        return parser.parse_args()



def get_timevalues(content):
        timestamplines = get_timelines(content)
        #Now remove the Unhelpful timezone from the lines and the #####
        timevalues = [line.split("GMT")[0][7:] for line in timestamplines]
        timevaluesastime=[datetime.datetime.strptime( line, __TIME_FORMAT) for line in timevalues]
        return timevaluesastime


def get_timelines(content):
        content = [line.replace("BST", "GMT") for line in content]
        content = [line.replace("BST", "GMT") for line in content]
        timestamplines = [line for line in content
                          if "GMT" in line if "#####" in line]
        return timestamplines


def getboundedcontentdic(content):
        boundedcontent = get_timelines(content)
        boundedsessionlines = [
            line for line in boundedcontent
            if "GMT" in line if " to " in line if "#####" in line]
        boundedsessiondic = {}
        for line in boundedsessionlines:
                start = line.split("GMT")[0][7:]
                end = line.split(" to ")[1][0:19]
                startts = datetime.datetime.strptime(start, __TIME_FORMAT)
                endts = datetime.datetime.strptime(end+" ", __TIME_FORMAT)
                boundedsessiondic[startts] = endts

        return boundedsessiondic


def get_title_of_session(content):
   for line in content:
                if "title: " in line:
                        return line.split(":")[1].strip()


def get_sessions(content, title, timestamp_extraction=get_timevalues):
        last = datetime.datetime.strptime(
            "11/07/2010-10:00:06 ", __TIME_FORMAT)
        current = last
        maybetitle=get_title_of_session(content)
        if (maybetitle):
            title=maybetitle
        boundedsessiondic = getboundedcontentdic(content)
        grouped_timevalues=[]
        current_group=[]
        for current in timestamp_extraction(content):
                if ((current-last) > datetime.timedelta(
                        minutes=max_dist_between_logs)):
                        grouped_timevalues.append(current_group)
                        current_group=[current]
                if current in boundedsessiondic:
                        last = boundedsessiondic[current]
                else:
                        last = current
                current_group.append(last)
        grouped_timevalues.append(current_group)
        sessions = []
        for i in grouped_timevalues:
            if i:
                if ((i[-1]-i[0])> datetime.timedelta(minutes=min_session_size)):
                    sessions.append(Session(title,i[0],i[-1],content))
        return sessions


def get_sessions_from_file_list(filelocations):
        sessions = []
        for location in filelocations:
                for file in glob.glob(location):
                        sessions.extend(get_sessions(icalhelper.get_content(file),file))
        return sessions


def projectreport(name, sessions, verbose):
        "Produce report for one project"
        project_sessions = [
            entry for entry in sessions if (
                entry.project == name)]
        total_time = sum([entry.length()
                          for entry in project_sessions], datetime.timedelta())
        if verbose:
                print "#### {}\n\nTotal Time on this project: {}\n".format(name.ljust(45), total_time)
                for entry in project_sessions:
                        print entry
        else:
                print "{}: {}".format(name.ljust(45), total_time)
        return total_time


def get_day_projects(sessions, today=datetime.datetime.today()):
        return [entry for entry in sessions if (
                entry.start.date() == today.date())]


def output_sessions_as_projects(sessions):
        total_time = sum([entry.length()
                          for entry in sessions], datetime.timedelta())
        projects = list(set([entry.project for entry in sessions]))
        for project in projects:
                projectreport(project, sessions, args.verbatim)
        print "Total project time".ljust(45)+str(total_time)


def calendar_output(sessions):
        cal = icalhelper.get_cal()
        for entry in sessions:
                icalhelper.add_event(cal, entry.project, entry.start, entry.end)
        print cal.to_ical()


# From SE
# http://stackoverflow.com/questions/13728392/moving-average-or-running-mean

# Running mean/Moving average
def get_running_mean(l, N):
        sum = 0
        result = list(0 for x in l)

        for i in range(0, N):
                sum = sum + l[i]
                result[i] = sum / (i+1)

        for i in range(N, len(l)):
                sum = sum - l[i-N] + l[i]
                result[i] = sum / N

        return result


def graph_out(sesssions,slug):
        DAY_COUNT = 26
        total_time = []
        for single_date in (
                datetime.datetime.today() - datetime.timedelta(days=n)
                for n in range(DAY_COUNT)):
                single_date_sessions = [
                    entry for entry in sessions if (
                        entry.start.date() == single_date.date())]
                element = int(
                              sum(
                                  [entry.length()
                                   for entry in single_date_sessions],
                                  datetime.timedelta()).total_seconds() / 60)
                total_time = [element]+total_time
        running_mean = get_running_mean(total_time, 7)
        write_to_javascript(total_time,running_mean,slug)

def write_to_javascript(total_time,running_mean,slug):
        f = open(vision_dir+"../javascript/"+slug+".js", 'wb')
        f.write(slug+"sessions=["+",".join(str(x) for x in total_time)+"];\n")
        f.write(slug+"running_mean=["+",".join(str(x) for x in running_mean)+"]")
        f.close()


if __name__ == "__main__":
        args = setup_argument_list()
        os.chdir(vision_dir)



        # sessions=process_project_file(vision_dir+"2017-04-01-tmc50private.md", [])
        # This is the line that compiles all of the information.
        filelocations = [vision_dir + x
                         for x in ["issues/*.md"]]
        sessions = get_sessions_from_file_list(filelocations)

        if args.target:
                print "target {}".format(args.target)
                sessions = get_sessions_from_file_list(
                    [x.replace("*", "*" + args.target + "*")
                     for x in filelocations])

        if args.action != "calendar":
                if args.action == "graph":
                        graph_out(sessions, "vision")

        """
    #### Work Graph
    Total Time on this project: 1:43:26

    ##### Sessions
        2016-08-12 06:16:26 to 06:36:32 (0:20:06)
        2016-08-12 07:58:21 to 09:21:41 (1:23:20)


    ### Summary for 2016-08-12
    Total project time  -     1:43:26"""

        if args.action == "today":
                output_sessions_as_projects(get_day_projects(sessions))

        if args.action == "all":
                output_sessions_as_projects(sessions)

        if args.action == "calendar":
                calendar_output(sessions)


        if args.action == "emailcal":
                sessions = get_sessions(icalhelper.get_content('/Users/josephreddington/Dropbox/git/DesktopTracking/output/results.txt'), "email", get_email_matches)
                #output_sessions_as_projects(sessions)
                calendar_output(sessions)

        if args.action == "email":
                sessions = get_sessions(icalhelper.get_content('/Users/josephreddington/Dropbox/git/DesktopTracking/output/results.txt'), "email", get_email_matches)
                output_sessions_as_projects(sessions)

        if args.action == "emailgraph":
                sessions = get_sessions(icalhelper.get_content('/Users/josephreddington/Dropbox/git/DesktopTracking/output/results.txt'), "email", get_email_matches)
                #output_sessions_as_projects(sessions)
                graph_out(sessions, "email")
