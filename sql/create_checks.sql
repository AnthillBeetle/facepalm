delimiter ;;

-- Do not try to use the following (commented) if's literally,
-- (won't work), just paste whatever is appropriate.
-- if version() >= '5.5' then

    create procedure signal5(signal_message_text text, signal_table_name text, signal_column_name text)
        signal sqlstate '45001'
        set
            message_text = signal_message_text,
            table_name = signal_table_name,
            column_name = signal_column_name;;

-- else

    create procedure signal5(signal_message_text text, signal_table_name text, signal_column_name text)
    begin
        call caught_signal(signal_message_text, signal_table_name, signal_column_name);
    end;;
    
-- end if;


create procedure contest_rounds_and_stages__check(
    new_contest int,
    new_round int,
    new_stage int,
    new_begins datetime,
    new_ends datetime)
begin
    declare overlap_round int;

    if new_begins >= new_ends then
        call signal5(
            concat('Round ', new_round, ' has non-positive duration.'),
            'contest_rounds_and_stages',
            'begins, ends');
    end if;

    select max(round) into overlap_round
    from contest_rounds_and_stages
    where
        contest = new_contest and
        round <> new_round and
        stage = new_stage and
        begins < new_ends and
        ends > new_begins;

    if overlap_round is not null then
        call signal5(
            concat('Rounds ', new_round, ' and ', overlap_round, ' overlap at stage ', new_stage, '.'),
            'current_and_future_stages',
            'begins, ends');
    end if;
end;;


create trigger contest_rounds_and_stages__insert_check
after insert on contest_rounds_and_stages
for each row
    call contest_rounds_and_stages__check(new.contest, new.round, new.stage, new.begins, new.ends);;

create trigger contest_rounds_and_stages__update_check
after update on contest_rounds_and_stages
for each row
    call contest_rounds_and_stages__check(new.contest, new.round, new.stage, new.begins, new.ends);;

