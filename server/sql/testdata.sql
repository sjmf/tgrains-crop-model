INSERT INTO tgrains.tags (id, name, `group`)
VALUES
(01, 'Small Business',            0),
(02, 'Food Poverty',              0),
(03, 'Consumption',               0),
(04, 'Social Media',              0),
(05, 'Education',                 0),
(06, 'Regulation',                0),
(07, 'Government',                0),
(08, 'Capitalism',                0),
(09, 'Profits',                   0),
(10, 'Middle-actors',             0),
(11, 'Wholesalers',               0),
(12, 'Climate Change',            0),
(13, 'Waste',                     0),
(14, 'Packaging',                 0),
(15, 'Expertise',                 0),
(16, 'Experience',                0),
(17, 'Organic',                   0),
(18, 'No-Till',                   0),

(19, 'Soft fruit',                1),
(20, 'Peas & Beans',              1),
(21, 'Oats',                      1),
(22, 'Sugar Beet',                1),
(23, 'Barley',                    1),
(24, 'Maize',                     1),
(25, 'Wheat',                     1),
(26, 'Vegetables',                1),
(27, 'Oilseed Rape',              1),
(28, 'Potatoes',                  1),
(29, 'Top fruit',                 1),

(30, 'Dairy Cattle',              1),
(31, 'Beef Cattle',               1),
(32, 'Chicken',                   1),
(33, 'Pork',                      1),
(34, 'Egg Production',            1),
(35, 'Lowland Lamb',              1),
(36, 'Upland Lamb',               1),

(37, 'Production',                2),
(38, 'Greenhouse Gas Emissions',  2),
(39, 'Nitrogen Leaching',         2),
(40, 'Profit',                    2),
(41, 'Calorie Production',        2),

(42, 'Pesticide Impacts',         3),
(43, 'Ground Water',              3),
(44, 'Fish',                      3),
(45, 'Birds',                     3),
(46, 'Bees',                      3),
(47, 'Beneficial Arthropods',     3),

(48, 'Nutrition',                 4),
(49, 'Vegetables',                4),
(50, 'Tubers',                    4),
(51, 'Whole Grains',              4),
(52, 'Plant Protein',             4),
(53, 'Animal Protein',            4),
(54, 'Added Sugars',              4),
(55, 'Added Fats',                4),
(56, 'Dairy',                     4),
(57, 'Fruit',                     4),

(58, 'Health',                    5),
(59, 'Stroke',                    5),
(60, 'Cancer',                    5),
(61, 'Heart Disease',             5),
(62, 'Diabetes',                  5);


INSERT INTO tgrains.comments (id, text, author, email, reply_id, timestamp, hash)
VALUES
(1, 'This is a comment. It is a sample comment demonstrating the social functionality of the TGRAINS scaled-up model prototype. Comment input is taken from the user, who may wish to link their social media accounts using the inbuilt functionality. Comments can also be tagged with features displayed in the model interface, and a set of pre-defined tags from the 2019 Workshop themes.', 'Samantha Finnigan', 'samantha@example.com', null, '2020-09-14 20:55:54', 'ab1dcca4b8b10fbc8515a8fa48843639aff953c14293e4e3440fd36a71714426'),
(2, 'Test', 'test', 'test@test.com', null, '2020-09-14 21:27:18', '3b8ce9097061d1d02d59f221973e2fed4e110babc93a0a9429e078464cf6cbc9'),
(3, 'This is another test. It&#39;s slightly shorter ;)', 'Testy McTestface', 'testy@mctestface.com', null, '2020-09-14 21:29:23', '89f9dec4741f4b0d65107f00053278b5ce884e4b190689d71bb0e61587440205'),
(4, '&lt;script type=&#34;text/html&#34;&gt;console.log(&#39;xss attempt&#39;)&lt;/script&gt;', 'Hackytester', 'hax@test.com', null, '2020-09-14 23:04:02', '770f5a578cbea8f72599f5715cdd3708d02167ac2ebae651894a29d848f6966e'),
(5, 'This is another comment. It is a sample comment demonstrating the social functionality of the TGRAINS scaled-up model prototype. Comment input is taken from the user, who may wish to link their social media accounts using the inbuilt functionality. Comments can also be tagged with features displayed in the model interface, and a set of pre-defined tags from the 2019 Workshop themes. ', 'Samantha', 'samantha@example.com', 1, '2020-09-14 23:17:39', 'ab1dcca4b8b10fbc8515a8fa48843639aff953c14293e4e3440fd36a71714426'),
(6, 'Hello! I&#39;m having great fun with this! Let&#39;s leave a comment! I can&#39;t attach it to a model state yet because that&#39;s not implemented, but I can move the sliders around and switch comment pages! I&#39;m particularly excited about this comment form and all the characters I can put in it! Ten thousand characters! Hooray! What fun! Wheeeee!', 'Charlie', 'sdfasdf', null, '2020-09-15 00:18:57', 'e8bd861ea77ae4a3772e124695ce0210bf210784a00084cea17537d3c5407191'),
(7, 'Some comment text!', 'Adrian', 'a@a.com', null, '2020-09-15 08:45:42', 'e39aef1b5148b276048a4f36f9219ada11dd3cda1d973823838e8e5ad466fad1'),
(8, 'Another test comment. We&#39;d like this one to appear without expanding the list of comments (prior server bug)', 'Samantha', 'samantha@example.com', null, '2020-09-15 16:25:36', 'ab1dcca4b8b10fbc8515a8fa48843639aff953c14293e4e3440fd36a71714426'),
(10, 'Here is a comment with lots of tags, to test the tag system! The tags should be:

Small Business, Middle-actors, No-till, Oilseed Rape, Beans, Sheep, Production, Whole Grains, Sugars, Health', 'Samantha Finnigan', 'sam.j.mf1@gmail.com', null, '2020-09-17 00:45:05', '68a9b929085f119165e60e88ff782a9b8f5b1cfda73b596e6cfbd5e252657337'),
(11, 'Here is another tag-testing comment. Tags are: Wholesalers, Wheat. I guess it&#39;s a comment about a mill!', 'Samantha', 's@j.mf', null, '2020-09-17 00:50:44', '3b503703696a496229cc791c036548a347484a337eb55a62e4da4d09531c1308');


INSERT INTO tgrains.comment_tags (comment_id, tag_id)
VALUES
(1,  4),
(1,  16),
(1,  21),
(3,  4),
(5,  6),
(10, 1),
(10, 10),
(10, 18),
(10, 20),
(10, 27),
(10, 36),
(10, 37),
(10, 51),
(10, 54),
(10, 58),
(11, 11),
(11, 25);