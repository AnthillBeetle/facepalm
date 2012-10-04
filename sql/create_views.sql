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

