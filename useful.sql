# levels where not all endings were achieved
select lvl.author, lvl.name, cut.name, cut.counter
from main_cutscene cut
left join main_level as lvl on lvl.id = cut.level_id
where lvl.id in
(select level_id
from main_cutscene
where ending = 1
group by level_id
having min(counter) = 0 and max(counter) > 0)
and ending = 1
order by lvl.author, lvl.name, cut.name;

# not verified levels with no endings at all but all cutscenes were achieved
select lvl.author, lvl.name, cut.name, cut.counter
from main_cutscene cut
left join main_level as lvl on lvl.id = cut.level_id
where lvl.id in
(select level_id
from main_cutscene
where ending = 0
group by level_id
having min(counter) > 0)
and lvl.id in
(select lr.level_id from main_levelrating lr where verified = 0)
and lvl.id not in
(select distinct level_id from main_cutscene where ending = 1)
order by lvl.author, lvl.name, cut.name;

# all verified levels (auto & set manually)
select lvl.author, lvl.name
from main_level lvl
left join main_levelrating as lr on lvl.id = lr.level_id
where verified = 1 or status > 4
order by lvl.author, lvl.name;


# levels completed by someone but not verified
select lvl.author, lvl.name
from main_level lvl
left join main_levelrating as lr on lvl.id = lr.level_id
where completions > 0 and verified = 0 and status <= 4
order by lvl.author, lvl.name;

# cutscenes of this levels
select name, author, action, cutscene, uid, time
from main_rate
where level_id in (select level_id from main_levelrating where completions > 0 and verified = 0 and status <= 4)
and action >= 4 and action != 7 and action != 8
order by author, name, time desc;

# achievements of this levels
select lvl.author, lvl.name, cut.name, cut.counter, cut.ending
from main_cutscene cut
left join main_level as lvl on lvl.id = cut.level_id
where level_id in (select level_id from main_levelrating where completions > 0 and verified = 0 and status <= 4)
order by lvl.author, lvl.name, cut.name;

# levels where some cutscenes were achieved and no endings (but they are exists)
select author, ml.name, sum(if(ending, counter, 0)) e, sum(if(ending, 0, counter)) c, sum(if(ending, 1, 0)) t
from main_cutscene mc
left join main_level ml on ml.id = mc.level_id
group by author, ml.name
having t > 0 and e = 0 and c > 0
order by c desc;