delete from votes;
delete from masterpieces;
delete from contest_categories;
delete from contests;
delete from users;


insert into user_roles(identifier, name) values('banned', 'бан');
insert into user_roles(identifier, name) values('anonymous', 'аноним');
insert into user_roles(identifier, name) values('registered', 'зарегистрированный пользователь');
insert into user_roles(identifier, name) values('administrator', 'администратор');

insert into user_actions(identifier, description) values('access', 'просматривать сайт');
insert into user_actions(identifier, description) values('register', 'регистрироваться');
insert into user_actions(identifier, description) values('vote', 'голосовать');
insert into user_actions(identifier, description) values('edit_profile', 'изменять профиль');
insert into user_actions(identifier, description) values('nominate', 'номинировать');
insert into user_actions(identifier, description) values('review_nominations', 'рецензировать номинации');
insert into user_actions(identifier, description) values('preview_results', 'просматривать предварительные результаты');

insert into user_roles_and_actions(role, action, is_allowed)
    select
        roles.id role,
        actions.id action,
        roles.identifier = 'administrator' or actions.identifier not in ('review_nominations', 'preview_results') and (
            roles.identifier = 'registered' or actions.identifier not in ('nominate', 'edit_profile') and (
                roles.identifier = 'anonymous' or actions.identifier not in ('access', 'vote', 'register')
            )
        ) is_allowed
    from
        user_roles roles,
        user_actions actions;

update user_roles_and_actions
set is_allowed = False
where
    role <> (select id from user_roles where identifier = 'anonymous') and
    action = (select id from user_actions where identifier = 'register');

-- select roles.identifier, actions.identifier, is_allowed from user_roles_and_actions allows, user_roles roles, user_actions actions where allows.role = roles.id and allows.action = actions.id;

insert into contests(godville_topic_id, identifier, name) values(2143, 'facepalm', 'Золотая Фейспальмовая ветвь');
insert into contests(godville_topic_id, identifier, name) values(2235, 'karoshi', 'Кароши люблю!');

insert into contest_stages(priority, identifier, description) values(1, 'publishing', 'публикация креатива');
insert into contest_stages(priority, identifier, description) values(2, 'nomination', 'номинирование креатива');
insert into contest_stages(priority, identifier, description) values(25, 'review', 'рецензирование номинаций');
insert into contest_stages(priority, identifier, description) values(3, 'voting', 'голосование');
insert into contest_stages(priority, identifier, description) values(4, 'results', 'вывешивание результатов');

set @contest_id = (select id from contests where identifier = 'facepalm');
insert into contest_categories(contest, is_grand_prix, priority, name, description) values(
    @contest_id,
    true,
    1,
    'Непревзойдённый фейспалм',
    'когда рука тянется к лицу буквально на чувственном уровне, креатив неописуемо бессмыслен, неправилен и неадекватен'
);
insert into contest_categories(contest, priority, name, description) values(
    @contest_id,
    2,
    'Ниже плинтуса',
    'шутки сортирного типа или направленные ниже пояса (обычный мат на конкурс не принимается, его надо просто флажковать)'
);
insert into contest_categories(contest, priority, name, description) values(
    @contest_id,
    3,
    'Интеллект так и прёт',
    'идеи, бездумно слепляющие в одно целое малосвязанные куски текста'
);
insert into contest_categories(contest, priority, name, description) values(
    @contest_id,
    4,
    'Негуманоидная логика',
    'бессмысленные наборы букв и идеи с неустранимыми логическими противоречиями'
);
insert into contest_categories(contest, priority, name, description) values(
    @contest_id,
    5,
    'Новая песня на старый лад',
    'идеи, которые уже многократно светились в ящике и были обсосаны до косточки, либо бородатые шутки, известные всем и без игры («Бояны»)'
);
insert into contest_categories(contest, priority, name, description) values(
    @contest_id,
    6,
    'Мисс Монстр',
    'Монстры Женского Рода («МЖР») — любому автору должно быть известно, что монстр обязан быть существительным мужского (либо общего) рода единственного числа'
);
insert into contest_categories(contest, priority, name, description) values(
    @contest_id,
    7,
    'Будет жирно и не слипнется',
    'фразы или активируемые трофеи, позволяющие легко получить много золотых кирпичей, кубиков праны, вылечить питомца, построить храм и т.д.'
);
insert into contest_categories(contest, priority, name, description) values(
    @contest_id,
    8,
    'Незамутнённое дарование',
    'тривиальнейшие идеи ясельного уровня (шутки про чукч и т.п.), часто со множеством грамматических ошибок'
);

set @contest_id = (select id from contests where identifier = 'karoshi');
-- insert into contest_categories(contest, priority, name, description) values(
--     @contest_id,
--     2,
--     'Лучший креатив',
--     'первичное голосование'
-- );
-- insert into contest_categories(contest, priority, name, description) values(
--     @contest_id,
--     4,
--     'Лучшая коррекция',
--     'операционная'
-- );
insert into contest_categories(contest, is_grand_prix, priority, name, description) values(
    @contest_id,
    True,
    2,
    'Кароши люблю',
    'лучшее из лучшего'
);

insert into ideabox_sections(priority, identifier, godville_section_name, short_name)
    values(1, 'diary', 'Фразы', 'Фраза');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name)
    values(2, 'status', 'Вести', 'Весть');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name)
    values(3, 'duel', 'Хроника дуэлей', 'Хроника');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name)
    values(4, 'quest', 'Задания', 'Задание');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name, prefix)
    values(5, 'monster', 'Монстры', 'Монстр', 'Монстр');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name, prefix)
    values(6, 'artifact', 'Трофеи', 'Трофей', 'Трофей');
insert into ideabox_sections(priority, identifier, godville_section_name, godville_subsection_name, short_name, prefix)
    values(70, 'weapon', 'Снаряжение', 'Оружие', 'Снаряжение/Оружие', 'Оружие');
insert into ideabox_sections(priority, identifier, godville_section_name, godville_subsection_name, short_name, prefix)
    values(71, 'shield', 'Снаряжение', 'Щит', 'Снаряжение/Щит', 'Щит');
insert into ideabox_sections(priority, identifier, godville_section_name, godville_subsection_name, short_name, prefix)
    values(72, 'head', 'Снаряжение', 'Голова', 'Снаряжение/Голова', 'Голова');
insert into ideabox_sections(priority, identifier, godville_section_name, godville_subsection_name, short_name, prefix)
    values(73, 'body', 'Снаряжение', 'Тело', 'Снаряжение/Тело', 'Тело');
insert into ideabox_sections(priority, identifier, godville_section_name, godville_subsection_name, short_name, prefix)
    values(74, 'arms', 'Снаряжение', 'Руки', 'Снаряжение/Руки', 'Руки');
insert into ideabox_sections(priority, identifier, godville_section_name, godville_subsection_name, short_name, prefix)
    values(75, 'legs', 'Снаряжение', 'Ноги', 'Снаряжение/Ноги', 'Ноги');
insert into ideabox_sections(priority, identifier, godville_section_name, godville_subsection_name, short_name, prefix)
    values(76, 'talisman', 'Снаряжение', 'Талисман', 'Снаряжение/Талисман', 'Талисман');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name, prefix)
    values(8, 'newspaper', 'Новости для газеты', 'Новость', 'Новость');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name, prefix)
    values(9, 'questionable', 'Сомнительный контент', 'Сомнительный контент', 'Обсуждаемое');
insert into ideabox_sections(priority, identifier, godville_section_name, short_name)
    values('A', 'other', 'Другое', 'Другое');

insert into ideabox_stages(priority, identifier, google_docs_name, name)
    values(1, 'voting', 'Первичное голосование', 'Голосование');
insert into ideabox_stages(priority, identifier, google_docs_name, name, clarification)
    values(2, 'correction', 'Операционная, коррекция', 'Коррекция', 'коррекция');
