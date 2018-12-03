from eAsistent_static import getCurrentSchoolWeek, getData

def prettyPrintChanges(specials_include=True, save_to_file=[True, False], log=False, full=False, week=getCurrentSchoolWeek()):
	ret_obj = getData(specials_include=specials_include, save_to_file=save_to_file, log=log, full=full, week=week)
	curr_week = getCurrentSchoolWeek()
	week_difference = week[0] - curr_week[0]
	base = "Exchanges in subjects in this week" if week_difference == 0 else "Exchanges in subjects in a week %i week%s away"%(week_difference, "s" if week_difference > 1 else "")
	if(ret_obj["specials"] == []):
		return "No %s."%base.lower()

	ret_ = "%s:\n"%base
	for t in ret_obj["specials"]:
		cur_sub = ret_obj["timetable"][t[0]]
		ret_ += "\t%s %s\n"%(cur_sub["time_print"], cur_sub["subject_abbr"])
	return ret_+"\n"

if __name__ == "__main__":
	print(prettyPrintChanges(save_to_file=[True, True], log=True))