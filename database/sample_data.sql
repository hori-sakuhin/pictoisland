-- Picto Island sample data
-- デモ用パスワードは3アカウント共通で sample1234
SET NAMES utf8mb4;
USE pictoisland;
START TRANSACTION;

DELETE gp FROM group_posts gp JOIN usergroups g ON g.id=gp.group_id WHERE g.group_name='なかよし島';
DELETE gm FROM group_members gm JOIN usergroups g ON g.id=gm.group_id WHERE g.group_name='なかよし島';
DELETE FROM usergroups WHERE group_name='なかよし島';
DELETE f FROM follows f JOIN accountdata a1 ON a1.id=f.follower_id JOIN accountdata a2 ON a2.id=f.followed_id WHERE a1.email IN ('island1@example.com','island2@example.com','island3@example.com') AND a2.email IN ('island1@example.com','island2@example.com','island3@example.com');
DELETE p FROM posts p JOIN accountdata a ON a.id=p.user_id WHERE a.email IN ('island1@example.com','island2@example.com','island3@example.com');
DELETE FROM accountdata WHERE email IN ('island1@example.com','island2@example.com','island3@example.com');

INSERT INTO accountdata (email,username,password_hash,is_public,comment,island_name,island_theme,house_image,island_image,icon_path) VALUES
('island1@example.com','island_user1','pbkdf2:sha256:600000$784d07f4521b3ef5$bde31d214da55b7b1bace8fff184383493a229cceeb34058976851bffff9d94e',1,'花と自然が好きです。島の写真を投稿しています。','フェアリー','自然・フェアリー','uploads/0b353a17-c5d5-47c2-8760-0f6f8ab5960b.png','islands/Island1.png','uploads/kabukiti_icon.png'),
('island2@example.com','island_user2','pbkdf2:sha256:600000$2cc38ad0b843d93a$e6ab756f1d10bcad2ad71a31e76dcb08340254f57a3a18a2132b93502f4396c5',1,'カフェ巡りと島づくりを楽しんでいます。','カフェ','カフェ・ナチュラル','uploads/63c464eb-9963-4bce-b6f3-03d0da8d2d5d.png','islands/island2.png','uploads/kamomi.jpg'),
('island3@example.com','island_user3','pbkdf2:sha256:600000$0c8bf73ba1d16268$71ebc8c1b96180b46f2a42e7afa0ccfaef2d34ba6d03e269e70c08d10c5b0514',1,'季節ごとに景色を変える島を作っています。','メープル','季節・かわいい','uploads/0b353a17-c5d5-47c2-8760-0f6f8ab5960b.png','islands/island3.png','uploads/me-puru.png');
SET @u1=(SELECT id FROM accountdata WHERE email='island1@example.com'); SET @u2=(SELECT id FROM accountdata WHERE email='island2@example.com'); SET @u3=(SELECT id FROM accountdata WHERE email='island3@example.com');
INSERT INTO posts (user_id,image_path,created_at) VALUES
(@u1,'uploads/8b4a473e-8087-499a-ae9e-49c2b7f0e996.jpg',NOW()-INTERVAL 2 HOUR),(@u1,'uploads/1d5cc7ff-239b-4273-b13d-f91e348132ce.jpg',NOW()-INTERVAL 2 DAY),
(@u2,'uploads/290db654-8888-40f1-a4ee-ef40813284fe.png',NOW()-INTERVAL 3 HOUR),(@u2,'uploads/kafe.jpeg',NOW()-INTERVAL 3 DAY),
(@u3,'uploads/8c7259c2-71ff-4535-8d77-ba4b657eaae0.png',NOW()-INTERVAL 4 HOUR),(@u3,'uploads/tenzi.jpg',NOW()-INTERVAL 4 DAY);
INSERT INTO follows (follower_id,followed_id,created_at) VALUES (@u1,@u2,NOW()),(@u2,@u1,NOW()),(@u1,@u3,NOW()),(@u3,@u1,NOW()),(@u2,@u3,NOW()),(@u3,@u2,NOW());
INSERT INTO usergroups (group_name,island_image,created_by) VALUES ('なかよし島','islands/island2.png',@u1); SET @g=LAST_INSERT_ID();
INSERT INTO group_members (group_id,user_id) VALUES (@g,@u1),(@g,@u2),(@g,@u3);
INSERT INTO group_posts (group_id,user_id,image_path,comment,created_at) VALUES
(@g,@u1,'uploads/8b4a473e-8087-499a-ae9e-49c2b7f0e996.jpg','みんなで島を散歩した日の思い出です。',NOW()-INTERVAL 3 DAY),
(@g,@u2,'uploads/290db654-8888-40f1-a4ee-ef40813284fe.png','お気に入りの場所で撮影しました。',NOW()-INTERVAL 2 DAY),
(@g,@u3,'uploads/tenzi.jpg','みんなで集まった記念写真です。',NOW()-INTERVAL 1 DAY);
COMMIT;
