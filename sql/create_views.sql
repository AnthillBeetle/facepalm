--- Copyright 2012 Anthill Beetle

--- This file is part of Facepalm web-engine.

--- Facepalm web-engine is free software: you can redistribute it and/or modify
--- it under the terms of the GNU General Public License as published by
--- the Free Software Foundation, either version 3 of the License, or
--- (at your option) any later version.

--- Facepalm web-engine is distributed in the hope that it will be useful,
--- but WITHOUT ANY WARRANTY; without even the implied warranty of
--- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--- GNU General Public License for more details.

--- You should have received a copy of the GNU General Public License
--- along with Facepalm web-engine. If not, see <http://www.gnu.org/licenses/>.

create view current_rounds as
    select *
    from current_and_future_rounds
    where not is_future;

create view current_and_future_stages as
    select
        rounds.is_future, stages.*
    from
        current_and_future_rounds rounds
        inner join contest_rounds_and_stages stages on
            rounds.round = stages.round and
            rounds.stage = stages.stage;


create view vote_multiples as
    select
        votes.contest_round,
        votes.contest_category,
        users.remote_address,
        count(1) multiple_count
    from
        votes, users
    where
        users.name is null and
        votes.user = users.id
    group by
        votes.contest_round,
        votes.contest_category,
        users.remote_address;

create view votes_info as
    select
        votes.*,
        users.name,
        users.remote_address,
        vote_multiples.multiple_count
    from
        votes inner join users on
            votes.user = users.id
        left join vote_multiples on
            votes.contest_round = vote_multiples.contest_round and
            votes.contest_category = vote_multiples.contest_category and
            users.remote_address = vote_multiples.remote_address;

create view round_results_view as
    select
        contest_round,
        contest_category,
        masterpiece,
        count(name)*2 registered_score,
        sum(if(name is null, 1.0/multiple_count, 2)) score
    from votes_info
    group by contest_round, contest_category, masterpiece;

