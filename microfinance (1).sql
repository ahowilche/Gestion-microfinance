-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mar. 17 juin 2025 à 07:58
-- Version du serveur : 10.4.28-MariaDB
-- Version de PHP : 8.1.17

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `microfinance`
--

-- --------------------------------------------------------

--
-- Structure de la table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add user', 6, 'add_agent'),
(22, 'Can change user', 6, 'change_agent'),
(23, 'Can delete user', 6, 'delete_agent'),
(24, 'Can view user', 6, 'view_agent'),
(25, 'Can add client', 7, 'add_client'),
(26, 'Can change client', 7, 'change_client'),
(27, 'Can delete client', 7, 'delete_client'),
(28, 'Can view client', 7, 'view_client'),
(29, 'Can add compte', 8, 'add_compte'),
(30, 'Can change compte', 8, 'change_compte'),
(31, 'Can delete compte', 8, 'delete_compte'),
(32, 'Can view compte', 8, 'view_compte'),
(33, 'Can add credit', 9, 'add_credit'),
(34, 'Can change credit', 9, 'change_credit'),
(35, 'Can delete credit', 9, 'delete_credit'),
(36, 'Can view credit', 9, 'view_credit'),
(37, 'Can add transaction', 10, 'add_transaction'),
(38, 'Can change transaction', 10, 'change_transaction'),
(39, 'Can delete transaction', 10, 'delete_transaction'),
(40, 'Can view transaction', 10, 'view_transaction'),
(41, 'Can add remboursement', 11, 'add_remboursement'),
(42, 'Can change remboursement', 11, 'change_remboursement'),
(43, 'Can delete remboursement', 11, 'delete_remboursement'),
(44, 'Can view remboursement', 11, 'view_remboursement'),
(45, 'Can add historique transaction', 12, 'add_historiquetransaction'),
(46, 'Can change historique transaction', 12, 'change_historiquetransaction'),
(47, 'Can delete historique transaction', 12, 'delete_historiquetransaction'),
(48, 'Can view historique transaction', 12, 'view_historiquetransaction'),
(49, 'Can add mouvement', 13, 'add_mouvement'),
(50, 'Can change mouvement', 13, 'change_mouvement'),
(51, 'Can delete mouvement', 13, 'delete_mouvement'),
(52, 'Can view mouvement', 13, 'view_mouvement');

-- --------------------------------------------------------

--
-- Structure de la table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `django_admin_log`
--

INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
(19, '2025-06-16 23:04:59.577432', '2', 'Paul Koffi', 3, '', 6, 5),
(20, '2025-06-16 23:08:28.038983', '6', 'agent1', 1, '[{\"added\": {}}]', 6, 5),
(21, '2025-06-16 23:09:24.389532', '6', 'KOUASSI PIERRE', 2, '[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\"]}}]', 6, 5),
(22, '2025-06-17 02:25:50.413962', '6', 'KOUASSI PIERRE', 3, '', 6, 5),
(23, '2025-06-17 03:16:52.425923', '31', 'mari Koffi (ID7555219)', 1, '[{\"added\": {}}]', 7, 5);

-- --------------------------------------------------------

--
-- Structure de la table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(6, 'gestion', 'agent'),
(7, 'gestion', 'client'),
(8, 'gestion', 'compte'),
(9, 'gestion', 'credit'),
(12, 'gestion', 'historiquetransaction'),
(13, 'gestion', 'mouvement'),
(11, 'gestion', 'remboursement'),
(10, 'gestion', 'transaction'),
(5, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Structure de la table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2025-05-24 16:57:06.968323'),
(2, 'contenttypes', '0002_remove_content_type_name', '2025-05-24 16:57:07.579756'),
(3, 'auth', '0001_initial', '2025-05-24 16:57:11.264175'),
(4, 'auth', '0002_alter_permission_name_max_length', '2025-05-24 16:57:11.922368'),
(5, 'auth', '0003_alter_user_email_max_length', '2025-05-24 16:57:11.953687'),
(6, 'auth', '0004_alter_user_username_opts', '2025-05-24 16:57:12.001552'),
(7, 'auth', '0005_alter_user_last_login_null', '2025-05-24 16:57:12.052045'),
(8, 'auth', '0006_require_contenttypes_0002', '2025-05-24 16:57:12.085355'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2025-05-24 16:57:12.127211'),
(10, 'auth', '0008_alter_user_username_max_length', '2025-05-24 16:57:12.164435'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2025-05-24 16:57:12.184954'),
(12, 'auth', '0010_alter_group_name_max_length', '2025-05-24 16:57:12.301914'),
(13, 'auth', '0011_update_proxy_permissions', '2025-05-24 16:57:12.345383'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2025-05-24 16:57:12.367654'),
(15, 'gestion', '0001_initial', '2025-05-24 16:57:22.912636'),
(16, 'admin', '0001_initial', '2025-05-24 16:57:25.341397'),
(17, 'admin', '0002_logentry_remove_auto_add', '2025-05-24 16:57:25.388271'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2025-05-24 16:57:25.451588'),
(19, 'sessions', '0001_initial', '2025-05-24 16:57:25.865051'),
(20, 'gestion', '0002_client_prenom', '2025-05-24 17:10:57.172588'),
(21, 'gestion', '0003_historiquetransaction_mouvement_and_more', '2025-06-04 18:45:55.679312'),
(22, 'gestion', '0004_client_agent_credit_agent_mouvement_agent', '2025-06-04 22:16:41.777880'),
(23, 'gestion', '0005_client_identifiant_alter_compte_client', '2025-06-10 15:26:53.110458'),
(24, 'gestion', '0006_compte_type_compte', '2025-06-14 01:09:06.252623'),
(25, 'gestion', '0007_alter_client_adresse', '2025-06-14 16:42:44.269259'),
(26, 'gestion', '0008_alter_mouvement_compte', '2025-06-15 17:38:20.610764'),
(27, 'gestion', '0009_credit_numero_credit', '2025-06-15 22:05:42.323578'),
(28, 'gestion', '0010_remboursement_agent_remboursement_methode_paiement_and_more', '2025-06-16 09:03:22.328192'),
(29, 'gestion', '0011_credit_montant_rembourse', '2025-06-16 13:49:12.604325'),
(30, 'gestion', '0012_alter_agent_role', '2025-06-16 21:46:07.466647'),
(31, 'gestion', '0013_alter_client_agent_alter_compte_client', '2025-06-16 23:56:04.679635'),
(32, 'gestion', '0014_historiquetransaction_agent_alter_compte_client', '2025-06-17 00:33:19.526303'),
(33, 'gestion', '0015_remove_credit_agent', '2025-06-17 00:41:41.999999'),
(34, 'gestion', '0016_remove_historiquetransaction_agent_credit_agent', '2025-06-17 00:45:19.815440'),
(35, 'gestion', '0017_historiquetransaction_agent', '2025-06-17 01:40:29.461904'),
(36, 'gestion', '0018_remove_historiquetransaction_agent', '2025-06-17 02:07:54.513613'),
(37, 'gestion', '0019_alter_agent_role', '2025-06-17 03:14:59.060571');

-- --------------------------------------------------------

--
-- Structure de la table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('126f4yv5mjq3rg5tq3kqbo0h4420ilxi', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMuRh:fej-e3DWgBXkpyiA4BbjKZ2e28jZTu1f-vqN2xgq2Zo', '2025-06-18 20:10:45.270415'),
('1878dy059ko8foaj3l9t5d4sdw60403a', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMwSC:RkoeFs_1HMd0JncLoAVYD3tsTyt27Qdp28H_wsuUKxg', '2025-06-18 22:19:24.066774'),
('1d500o1c22kb1ep1t7ir1a9j1z0ep65t', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMZn7:QWEMFINeQSKxFCP9x2IdR2icBlK3WAwyJo7hyhZPeS0', '2025-06-17 22:07:29.124414'),
('2ppage3c160cmcuy3omgodbna34dedjl', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uP0vZ:H1pI9rw2Z5x2w9Y2OwO9vxMtGk_GxdJoaUEjYQkO0Rc', '2025-06-24 15:30:17.376718'),
('6ca6wu97mwgiqwbz9fxpaf1mub2f7re8', '.eJxVjEEOwiAQRe_C2hBA6Exduu8ZyACDVA0kpV0Z765NutDtf-_9l_C0rcVvnRc_J3ERRpx-t0DxwXUH6U711mRsdV3mIHdFHrTLqSV-Xg_376BQL986aJOtTaMiVGcbAfLICCkislUuD5ED2agwOyRFYLQiN0AwgDozIIv3B-PpN-I:1uQLqf:I_QXueoKNO_LzNL1DDURLCpsSrKPtZfU7UXEQpyEpZY', '2025-06-28 08:02:45.598897'),
('8s90qpuqt3ew3bkk3oy365jj3dkl2pvi', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uIsIU:T_QLdaGiOAYAYij_8aRF446NrulVdkv96JauHSE6IqU', '2025-06-07 17:04:34.630913'),
('bo5o0ne7i6qvgttwe4pu0weld1iv2zzn', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uOTVs:MNfoNd5gNndO_j06tX09zhlj1elajPyVnu6yhMsv93c', '2025-06-23 03:49:32.432235'),
('d5kuszv9mxqgps624mxmeu1mkx3fgloh', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uQpt4:jx9SQBkznkeXhlb4YHPnfjZjot_33Eqf9Z9kA6XE_4A', '2025-06-29 16:07:14.979907'),
('dnvz11thtqusfxorypqijlz17uvnd4nb', '.eJxVjEEOwiAQRe_C2hBA6Exduu8ZyACDVA0kpV0Z765NutDtf-_9l_C0rcVvnRc_J3ERRpx-t0DxwXUH6U711mRsdV3mIHdFHrTLqSV-Xg_376BQL986aJOtTaMiVGcbAfLICCkislUuD5ED2agwOyRFYLQiN0AwgDozIIv3B-PpN-I:1uQqo9:z83shOe2saWgemjUf74KjSpMGccLFfWJu-zXBOdcUkw', '2025-06-29 17:06:13.998104'),
('dzoo0audyndjj6tcts67mjchnvm3s0t5', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uRINM:jPbTcJt-Yely5OVEgMumMRzbOFQPHniW2Mlc_Y9ygis', '2025-06-30 22:32:24.434240'),
('g0o7jc84yc0etgeqdzfgecwsrgmpeqdq', '.eJxVjDsOwjAQBe_iGllxduM4lPScIdpfSADZUj4V4u4QKQW0b2bey_W0rWO_LTb3k7qzQ3f63ZjkYXkHeqd8K15KXueJ_a74gy7-WtSel8P9OxhpGb81JIRAcQhsyClGCigGamIpVFFBmGNd48AgWkFrSNokYMQhUNs1nXt_APCVOCk:1uRMrV:RENYP933_06A5TOVql3_ax8ucK8lheKmsWIXScgdeeQ', '2025-07-01 03:19:49.920188'),
('g396ebrcgx7zzlwgy2kewh266fjhj5zu', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMtrN:aG3HU5Zkfz0SStpgIV9yxmyNH6m0QDriF3aAR-m_edo', '2025-06-18 19:33:13.361626'),
('hb3eumr2acp8pi8ghe3nq6ysc3qi4cg2', '.eJxVjDsOwjAQBe_iGllxduM4lPScIdpfSADZUj4V4u4QKQW0b2bey_W0rWO_LTb3k7qzQ3f63ZjkYXkHeqd8K15KXueJ_a74gy7-WtSel8P9OxhpGb81JIRAcQhsyClGCigGamIpVFFBmGNd48AgWkFrSNokYMQhUNs1nXt_APCVOCk:1uRKKq:OZJmkBW7RVr_aprJ_mujbaLX-gbmLNAvNKwtif2p0XA', '2025-07-01 00:37:56.568756'),
('jumgny2so6mbzk4bebitin5jj7llhca8', '.eJxVjEEOwiAQRe_C2hBA6Exduu8ZyACDVA0kpV0Z765NutDtf-_9l_C0rcVvnRc_J3ERRpx-t0DxwXUH6U711mRsdV3mIHdFHrTLqSV-Xg_376BQL986aJOtTaMiVGcbAfLICCkislUuD5ED2agwOyRFYLQiN0AwgDozIIv3B-PpN-I:1uQG7c:HqVioDjJXBnLkp5EJRur_5byBucfkJjKhgjlxBABTPo', '2025-06-28 01:55:52.464948'),
('lm5ub2armtea8gytcsef2toadpuy9lh9', '.eJxVjEEOwiAQRe_C2hBA6Exduu8ZyACDVA0kpV0Z765NutDtf-_9l_C0rcVvnRc_J3ERRpx-t0DxwXUH6U711mRsdV3mIHdFHrTLqSV-Xg_376BQL986aJOtTaMiVGcbAfLICCkislUuD5ED2agwOyRFYLQiN0AwgDozIIv3B-PpN-I:1uQTAF:64HwcOvX2hKhjib2Js79eyfyH9eeuy75S1E_LG6A5TA', '2025-06-28 15:51:27.299433'),
('nt0b33ubi60bwhfzvk221zoejfxo57dm', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMuEr:oMp521JvtyfkUzhM11vOIMUkV_wLLsiFODEIkmMI2z0', '2025-06-18 19:57:29.324943'),
('qgq7hbhk4bm3iyzpt2wtvjknlap9z98s', '.eJxVjDsOwjAQBe_iGlm2s86uKek5g7X-4QBypDipEHeHSCmgfTPzXsLztla_9bz4KYmzGMXpdwscH7ntIN253WYZ57YuU5C7Ig_a5XVO-Xk53L-Dyr1-a3JO6WIQKY_FglIRI1uNHBjYDBQsGU0ZHVIAIAMxO-3KEFQqgAnE-wPDSDcv:1uRJ64:AjY2QsdXZVwa_D1xY4Xqy85V5ZoR5dpISHGc-8BxC8I', '2025-06-30 23:18:36.437714'),
('s4y7shbbdu9pwxb62wsor8p4mslqbu1z', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMtrN:aG3HU5Zkfz0SStpgIV9yxmyNH6m0QDriF3aAR-m_edo', '2025-06-18 19:33:13.333575'),
('tp7l7jhrm5blwsstqtzvz1qruxl03wk1', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMwSC:RkoeFs_1HMd0JncLoAVYD3tsTyt27Qdp28H_wsuUKxg', '2025-06-18 22:19:24.095407'),
('z4n89m67hd26yvgbfo5q1ffsaybezp26', '.eJxVjDEOwjAMRe-SGUWOU3DCyM4ZIid2SQG1UtNOiLtDpQ6w_vfef5nE61LT2nROg5izcebwu2UuDx03IHceb5Mt07jMQ7abYnfa7HUSfV529--gcqvf2ouLGgSACGIIhZhOTH2Ogv5IPauQJ1BAx8iYuwBOPWKHAEU8qHl_AM8kNys:1uMwOa:io5VIG_x1oWpikHmb1FAoKMF8rPxDNd2E5GawAhJA4A', '2025-06-18 22:15:40.658708');

-- --------------------------------------------------------

--
-- Structure de la table `gestion_agent`
--

CREATE TABLE `gestion_agent` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `gestion_agent`
--

INSERT INTO `gestion_agent` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`, `role`) VALUES
(4, 'pbkdf2_sha256$600000$xIiUvYuvaHKPTEoOPC6IM3$z0MwbgBRJOGowcMTytmdCsWMG2oTXrUyfNe6Jrtf6BY=', '2025-06-17 03:19:49.847981', 0, 'superviseur', 'AHOLIA', 'ADJI', 'aholiacherel@gmail.com', 0, 1, '2025-06-16 22:57:28.000000', 'superviseur'),
(5, 'pbkdf2_sha256$600000$IGUq7O8VpbyjvTjLjdx4u3$bMlM4bvAEHLPqEE1R5r3K51zQ/KldYR2txwu/H0ZXFM=', '2025-06-17 03:15:37.189580', 1, 'Microfinance', '', '', 'aholiacherel@gmail.com', 1, 1, '2025-06-16 23:00:42.039568', 'agent');

-- --------------------------------------------------------

--
-- Structure de la table `gestion_agent_groups`
--

CREATE TABLE `gestion_agent_groups` (
  `id` bigint(20) NOT NULL,
  `agent_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `gestion_agent_user_permissions`
--

CREATE TABLE `gestion_agent_user_permissions` (
  `id` bigint(20) NOT NULL,
  `agent_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `gestion_client`
--

CREATE TABLE `gestion_client` (
  `id` bigint(20) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `telephone` varchar(20) NOT NULL,
  `adresse` varchar(150) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `date_inscription` date NOT NULL,
  `email` varchar(254) DEFAULT NULL,
  `agent_id` bigint(20) NOT NULL,
  `identifiant` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `gestion_client`
--

INSERT INTO `gestion_client` (`id`, `nom`, `telephone`, `adresse`, `prenom`, `date_inscription`, `email`, `agent_id`, `identifiant`) VALUES
(15, 'Tuo', '0104550613', 'Taabo,Commune', 'Mohamed', '2025-06-17', 'mohamed@outlook.com', 4, 'ID9937337'),
(16, 'Gogoua', '0798884421', 'Grand-Bassam', 'Pierre', '2025-06-17', 'mermoz@gmail.com', 4, 'ID6302582'),
(17, 'Dupont', '+2250700123456', '12 Rue des Fleurs, Abidjan', 'Jean', '2025-06-17', 'jean.dupont@example.com', 4, 'ID5915646'),
(19, 'Traoré', '+2250700654321', '5 Avenue de la Paix, Yamoussoukro', 'Aminata', '2025-06-17', 'aminata.traore@example.com', 4, 'ID7734452'),
(20, 'Kone', '+2250700102030', '10 Allée des Roses, Aboisso', 'Salimata', '2025-06-17', 'salimata.kone@example.com', 4, 'ID0018472'),
(21, 'Diaby', '+2250700998877', '4 Place du Marché, Gagnoa', 'Safi', '2025-06-17', 'safi.diaby@example.com', 4, 'ID5257033'),
(22, 'Diaby', '+2250700998877', '4 Place du Marché, Gagnoa', 'Safi', '2025-06-17', 'safi.diaby@example.com', 4, 'ID6325743'),
(23, 'Ouattara', '+2250700332211', '20 Rue des Artistes, Abidjan', 'Aïcha', '2025-06-17', 'aicha.ouattara@example.com', 4, 'ID1745386'),
(24, 'Diallo', '+2250700445566', '1 Impasse des Palmiers, Korhogo', 'Fatou', '2025-06-17', 'fatou.diallo@example.com', 4, 'ID9849308'),
(25, 'Doumbia', '+2250700223344', '1 Allée des Baobabs, Bouaké', 'Fatoumata', '2025-06-17', 'fatou.doumbia@example.com', 4, 'ID7132621'),
(26, 'Diop', '+2250700556677', '9 Rue du Foyer, Korhogo', 'Moussa', '2025-06-17', 'moussa.soro@example.com', 4, 'ID8229227'),
(27, 'Dao', '+2250700889900', '14 Boulevard du Port, Abidjan', 'Awa', '2025-06-17', 'awa.dao@example.com', 4, 'ID2354350'),
(28, 'Kouame', '+2250700121212', '2 Rue des Écoles, Daloa', 'Patrick', '2025-06-17', 'patrick.kouame@example.com', 4, 'ID8206639'),
(29, 'Kone', '+2250700121212', 'Pharmacie Etoile, Abobo', 'Aboudramane', '2025-06-17', 'kone@gmail.com', 4, 'ID9303148'),
(30, 'Sekongo', '0546110591', 'Port-Bouët', 'yely', '2025-06-17', 'yeli@gmail.com', 4, 'ID5889929'),
(31, 'mari', '0546110591', 'ABOBO, Sogephia', 'Koffi', '2025-06-17', 'mk@example.com', 4, 'ID7555219');

-- --------------------------------------------------------

--
-- Structure de la table `gestion_compte`
--

CREATE TABLE `gestion_compte` (
  `id` bigint(20) NOT NULL,
  `solde` decimal(12,2) NOT NULL,
  `client_id` bigint(20) NOT NULL,
  `date_creation` date NOT NULL,
  `numero_compte` varchar(20) NOT NULL,
  `type_compte` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `gestion_compte`
--

INSERT INTO `gestion_compte` (`id`, `solde`, `client_id`, `date_creation`, `numero_compte`, `type_compte`) VALUES
(21, 4700.00, 15, '2025-06-17', 'C-202506174244', 'epargne'),
(22, 8000.00, 16, '2025-06-17', 'C-202506171723', 'epargne'),
(23, 14100.00, 17, '2025-06-17', 'C-202506174935', 'epargne'),
(24, 79500.00, 19, '2025-06-17', 'C-202506178735', 'epargne'),
(25, 0.00, 20, '2025-06-17', 'C-202506174689', 'epargne'),
(26, 0.00, 21, '2025-06-17', 'C-202506178905', 'epargne'),
(27, 0.00, 22, '2025-06-17', 'C-202506173428', 'epargne'),
(28, 0.00, 23, '2025-06-17', 'C-202506174865', 'epargne'),
(29, 0.00, 24, '2025-06-17', 'C-202506177983', 'epargne'),
(30, 2000.00, 19, '2025-06-17', 'C-202506176336', 'courant'),
(31, 4500.00, 23, '2025-06-17', 'C-202506174683', 'courant'),
(32, 5500.00, 25, '2025-06-17', 'C-202506172550', 'epargne'),
(33, 5000.00, 26, '2025-06-17', 'C-202506177279', 'epargne'),
(34, 170000.00, 27, '2025-06-17', 'C-202506174119', 'epargne'),
(35, 0.00, 28, '2025-06-17', 'C-202506174485', 'epargne'),
(36, 0.00, 29, '2025-06-17', 'C-202506177190', 'epargne'),
(37, 7020.00, 17, '2025-06-17', 'C-202506175607', 'courant'),
(38, 7000.00, 29, '2025-06-17', 'C-202506175291', 'courant'),
(39, 10000.00, 30, '2025-06-17', 'C-202506174050', 'epargne'),
(40, 0.00, 31, '2025-06-17', 'C-202506173729', 'epargne');

-- --------------------------------------------------------

--
-- Structure de la table `gestion_credit`
--

CREATE TABLE `gestion_credit` (
  `id` bigint(20) NOT NULL,
  `montant` decimal(12,2) NOT NULL,
  `taux_interet` decimal(5,2) NOT NULL,
  `statut` varchar(20) NOT NULL,
  `compte_id` bigint(20) NOT NULL,
  `date_octroi` date NOT NULL,
  `duree_mois` int(10) UNSIGNED NOT NULL CHECK (`duree_mois` >= 0),
  `numero_credit` varchar(50) NOT NULL,
  `montant_rembourse` decimal(12,2) NOT NULL,
  `agent_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `gestion_credit`
--

INSERT INTO `gestion_credit` (`id`, `montant`, `taux_interet`, `statut`, `compte_id`, `date_octroi`, `duree_mois`, `numero_credit`, `montant_rembourse`, `agent_id`) VALUES
(17, 1500.00, 3.00, 'EN_COURS', 21, '2025-06-17', 12, 'CR-20250617023414164739', 0.00, 4),
(18, 40000.00, 4.00, 'EN_COURS', 24, '2025-06-17', 32, 'CR-20250617030150250287', 0.00, 4),
(19, 5000.00, 1.20, 'EN_COURS', 33, '2025-06-17', 12, 'CR-20250617030207046717', 0.00, 4),
(20, 42000.00, 2.00, 'EN_COURS', 24, '2025-06-17', 34, 'CR-20250617030232557051', 0.00, 4),
(21, 345000.00, 5.00, 'EN_COURS', 34, '2025-06-17', 15, 'CR-20250617030258617855', 0.00, 4),
(22, 3000.00, 1.20, 'EN_COURS', 21, '2025-06-17', 8, 'CR-20250617030321995197', 0.00, 4),
(23, 1100.00, 2.00, 'EN_COURS', 23, '2025-06-17', 23, 'CR-20250617053513953666', 0.00, 4);

-- --------------------------------------------------------

--
-- Structure de la table `gestion_historiquetransaction`
--

CREATE TABLE `gestion_historiquetransaction` (
  `id` bigint(20) NOT NULL,
  `type_operation` varchar(20) NOT NULL,
  `montant` decimal(12,2) NOT NULL,
  `date` datetime(6) NOT NULL,
  `description` longtext NOT NULL,
  `compte_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `gestion_historiquetransaction`
--

INSERT INTO `gestion_historiquetransaction` (`id`, `type_operation`, `montant`, `date`, `description`, `compte_id`) VALUES
(46, 'DEPOT', 2000.00, '2025-06-17 02:33:37.039531', 'DEPOT effectué par AHOLIA ADJI', 21),
(47, 'DEPOT', 10000.00, '2025-06-17 02:33:48.375096', 'DEPOT effectué par AHOLIA ADJI', 22),
(48, 'RETRAIT', 2000.00, '2025-06-17 02:33:56.301962', 'RETRAIT effectué par AHOLIA ADJI', 22),
(49, 'CREDIT', 1500.00, '2025-06-17 02:34:14.215150', 'Crédit octroyé (Numéro: CR-20250617023414164739)', 21),
(50, 'REMBOURSEMENT', 800.00, '2025-06-17 02:34:32.268162', 'Remboursement crédit (REM-20250617023432185639) - Principal: 800, Intérêts: 0.00', 21),
(51, 'RETRAIT', 3000.00, '2025-06-17 02:59:52.224624', 'RETRAIT effectué par AHOLIA ADJI', 38),
(52, 'RETRAIT', 1000.00, '2025-06-17 03:00:01.624725', 'RETRAIT effectué par AHOLIA ADJI', 21),
(53, 'DEPOT', 5500.00, '2025-06-17 03:00:23.285222', 'DEPOT effectué par AHOLIA ADJI', 32),
(54, 'DEPOT', 20000.00, '2025-06-17 03:00:49.229718', 'DEPOT effectué par AHOLIA ADJI', 23),
(55, 'RETRAIT', 7000.00, '2025-06-17 03:01:09.732196', 'RETRAIT effectué par AHOLIA ADJI', 23),
(56, 'CREDIT', 40000.00, '2025-06-17 03:01:50.422091', 'Crédit octroyé (Numéro: CR-20250617030150250287)', 24),
(57, 'CREDIT', 5000.00, '2025-06-17 03:02:07.095512', 'Crédit octroyé (Numéro: CR-20250617030207046717)', 33),
(58, 'CREDIT', 42000.00, '2025-06-17 03:02:32.608755', 'Crédit octroyé (Numéro: CR-20250617030232557051)', 24),
(59, 'CREDIT', 345000.00, '2025-06-17 03:02:58.617855', 'Crédit octroyé (Numéro: CR-20250617030258617855)', 34),
(60, 'CREDIT', 3000.00, '2025-06-17 03:03:22.063585', 'Crédit octroyé (Numéro: CR-20250617030321995197)', 21),
(61, 'DEPOT', 10000.00, '2025-06-17 03:04:39.610151', 'DEPOT effectué par AHOLIA ADJI', 39),
(62, 'REMBOURSEMENT', 150000.00, '2025-06-17 03:05:12.833843', 'Remboursement crédit (REM-20250617030512703157) - Principal: 150000, Intérêts: 0.00', 34),
(63, 'REMBOURSEMENT', 2500.00, '2025-06-17 03:05:32.522663', 'Remboursement crédit (REM-20250617030532456782) - Principal: 2500, Intérêts: 0.00', 24),
(64, 'RETRAIT', 25000.00, '2025-06-17 05:32:31.288729', 'RETRAIT effectué par AHOLIA ADJI', 34),
(65, 'CREDIT', 1100.00, '2025-06-17 05:35:14.113593', 'Crédit octroyé (Numéro: CR-20250617053513953666)', 23);

-- --------------------------------------------------------

--
-- Structure de la table `gestion_mouvement`
--

CREATE TABLE `gestion_mouvement` (
  `id` bigint(20) NOT NULL,
  `type_mouvement` varchar(10) NOT NULL,
  `montant` decimal(10,2) NOT NULL,
  `date` datetime(6) NOT NULL,
  `compte_id` bigint(20) NOT NULL,
  `agent_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `gestion_mouvement`
--

INSERT INTO `gestion_mouvement` (`id`, `type_mouvement`, `montant`, `date`, `compte_id`, `agent_id`) VALUES
(25, 'DEPOT', 2000.00, '2025-06-17 02:33:36.992658', 21, 4),
(26, 'DEPOT', 10000.00, '2025-06-17 02:33:48.254436', 22, 4),
(27, 'RETRAIT', 2000.00, '2025-06-17 02:33:56.286804', 22, 4),
(28, 'RETRAIT', 3000.00, '2025-06-17 02:59:52.084238', 38, 4),
(29, 'RETRAIT', 1000.00, '2025-06-17 03:00:01.624725', 21, 4),
(30, 'DEPOT', 5500.00, '2025-06-17 03:00:22.968353', 32, 4),
(31, 'DEPOT', 20000.00, '2025-06-17 03:00:49.214829', 23, 4),
(32, 'RETRAIT', 7000.00, '2025-06-17 03:01:09.475016', 23, 4),
(33, 'DEPOT', 10000.00, '2025-06-17 03:04:39.559644', 39, 4),
(34, 'RETRAIT', 25000.00, '2025-06-17 05:32:31.147351', 34, 4);

-- --------------------------------------------------------

--
-- Structure de la table `gestion_remboursement`
--

CREATE TABLE `gestion_remboursement` (
  `id` bigint(20) NOT NULL,
  `montant` decimal(10,2) NOT NULL,
  `credit_id` bigint(20) NOT NULL,
  `date` datetime(6) NOT NULL,
  `agent_id` bigint(20) DEFAULT NULL,
  `methode_paiement` varchar(50) NOT NULL,
  `montant_interet` decimal(10,2) NOT NULL,
  `montant_principal` decimal(10,2) NOT NULL,
  `notes` longtext DEFAULT NULL,
  `numero_remboursement` varchar(50) NOT NULL,
  `reference` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `gestion_remboursement`
--

INSERT INTO `gestion_remboursement` (`id`, `montant`, `credit_id`, `date`, `agent_id`, `methode_paiement`, `montant_interet`, `montant_principal`, `notes`, `numero_remboursement`, `reference`) VALUES
(14, 800.00, 17, '2025-06-17 00:00:00.000000', 4, 'ESPECES', 0.00, 800.00, '', 'REM-20250617023432185639', ''),
(15, 150000.00, 21, '2025-06-17 00:00:00.000000', 4, 'MOBILE_MONEY', 0.00, 150000.00, '', 'REM-20250617030512703157', ''),
(16, 2500.00, 18, '2025-06-17 00:00:00.000000', 4, 'ESPECES', 0.00, 2500.00, '', 'REM-20250617030532456782', '');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Index pour la table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Index pour la table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Index pour la table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_gestion_agent_id` (`user_id`);

--
-- Index pour la table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Index pour la table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Index pour la table `gestion_agent`
--
ALTER TABLE `gestion_agent`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Index pour la table `gestion_agent_groups`
--
ALTER TABLE `gestion_agent_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `gestion_agent_groups_agent_id_group_id_73bb9073_uniq` (`agent_id`,`group_id`),
  ADD KEY `gestion_agent_groups_group_id_6ec488ac_fk_auth_group_id` (`group_id`);

--
-- Index pour la table `gestion_agent_user_permissions`
--
ALTER TABLE `gestion_agent_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `gestion_agent_user_permi_agent_id_permission_id_a6c7a0f9_uniq` (`agent_id`,`permission_id`),
  ADD KEY `gestion_agent_user_p_permission_id_0dee0699_fk_auth_perm` (`permission_id`);

--
-- Index pour la table `gestion_client`
--
ALTER TABLE `gestion_client`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `identifiant` (`identifiant`),
  ADD KEY `gestion_client_agent_id_dbca859c_fk_gestion_agent_id` (`agent_id`);

--
-- Index pour la table `gestion_compte`
--
ALTER TABLE `gestion_compte`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_compte` (`numero_compte`),
  ADD KEY `gestion_compte_client_id_27f907b9` (`client_id`);

--
-- Index pour la table `gestion_credit`
--
ALTER TABLE `gestion_credit`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_credit` (`numero_credit`),
  ADD KEY `gestion_credit_compte_id_b2ccade1_fk_gestion_compte_id` (`compte_id`),
  ADD KEY `gestion_credit_agent_id_4a24a73d_fk_gestion_agent_id` (`agent_id`);

--
-- Index pour la table `gestion_historiquetransaction`
--
ALTER TABLE `gestion_historiquetransaction`
  ADD PRIMARY KEY (`id`),
  ADD KEY `gestion_historiquetr_compte_id_2f1b968a_fk_gestion_c` (`compte_id`);

--
-- Index pour la table `gestion_mouvement`
--
ALTER TABLE `gestion_mouvement`
  ADD PRIMARY KEY (`id`),
  ADD KEY `gestion_mouvement_compte_id_6ca85fb2_fk_gestion_compte_id` (`compte_id`),
  ADD KEY `gestion_mouvement_agent_id_03740039_fk_gestion_agent_id` (`agent_id`);

--
-- Index pour la table `gestion_remboursement`
--
ALTER TABLE `gestion_remboursement`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_remboursement` (`numero_remboursement`),
  ADD KEY `gestion_remboursement_credit_id_f0108c20_fk_gestion_credit_id` (`credit_id`),
  ADD KEY `gestion_remboursement_agent_id_e78f9260_fk_gestion_agent_id` (`agent_id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT pour la table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT pour la table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT pour la table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=38;

--
-- AUTO_INCREMENT pour la table `gestion_agent`
--
ALTER TABLE `gestion_agent`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `gestion_agent_groups`
--
ALTER TABLE `gestion_agent_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `gestion_agent_user_permissions`
--
ALTER TABLE `gestion_agent_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `gestion_client`
--
ALTER TABLE `gestion_client`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT pour la table `gestion_compte`
--
ALTER TABLE `gestion_compte`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT pour la table `gestion_credit`
--
ALTER TABLE `gestion_credit`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT pour la table `gestion_historiquetransaction`
--
ALTER TABLE `gestion_historiquetransaction`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=66;

--
-- AUTO_INCREMENT pour la table `gestion_mouvement`
--
ALTER TABLE `gestion_mouvement`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT pour la table `gestion_remboursement`
--
ALTER TABLE `gestion_remboursement`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Contraintes pour la table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Contraintes pour la table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_gestion_agent_id` FOREIGN KEY (`user_id`) REFERENCES `gestion_agent` (`id`);

--
-- Contraintes pour la table `gestion_agent_groups`
--
ALTER TABLE `gestion_agent_groups`
  ADD CONSTRAINT `gestion_agent_groups_agent_id_6bc02ef7_fk_gestion_agent_id` FOREIGN KEY (`agent_id`) REFERENCES `gestion_agent` (`id`),
  ADD CONSTRAINT `gestion_agent_groups_group_id_6ec488ac_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Contraintes pour la table `gestion_agent_user_permissions`
--
ALTER TABLE `gestion_agent_user_permissions`
  ADD CONSTRAINT `gestion_agent_user_p_agent_id_5dc97504_fk_gestion_a` FOREIGN KEY (`agent_id`) REFERENCES `gestion_agent` (`id`),
  ADD CONSTRAINT `gestion_agent_user_p_permission_id_0dee0699_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);

--
-- Contraintes pour la table `gestion_client`
--
ALTER TABLE `gestion_client`
  ADD CONSTRAINT `gestion_client_agent_id_dbca859c_fk_gestion_agent_id` FOREIGN KEY (`agent_id`) REFERENCES `gestion_agent` (`id`);

--
-- Contraintes pour la table `gestion_compte`
--
ALTER TABLE `gestion_compte`
  ADD CONSTRAINT `gestion_compte_client_id_27f907b9_fk_gestion_client_id` FOREIGN KEY (`client_id`) REFERENCES `gestion_client` (`id`);

--
-- Contraintes pour la table `gestion_credit`
--
ALTER TABLE `gestion_credit`
  ADD CONSTRAINT `gestion_credit_agent_id_4a24a73d_fk_gestion_agent_id` FOREIGN KEY (`agent_id`) REFERENCES `gestion_agent` (`id`),
  ADD CONSTRAINT `gestion_credit_compte_id_b2ccade1_fk_gestion_compte_id` FOREIGN KEY (`compte_id`) REFERENCES `gestion_compte` (`id`);

--
-- Contraintes pour la table `gestion_historiquetransaction`
--
ALTER TABLE `gestion_historiquetransaction`
  ADD CONSTRAINT `gestion_historiquetr_compte_id_2f1b968a_fk_gestion_c` FOREIGN KEY (`compte_id`) REFERENCES `gestion_compte` (`id`);

--
-- Contraintes pour la table `gestion_mouvement`
--
ALTER TABLE `gestion_mouvement`
  ADD CONSTRAINT `gestion_mouvement_agent_id_03740039_fk_gestion_agent_id` FOREIGN KEY (`agent_id`) REFERENCES `gestion_agent` (`id`),
  ADD CONSTRAINT `gestion_mouvement_compte_id_6ca85fb2_fk_gestion_compte_id` FOREIGN KEY (`compte_id`) REFERENCES `gestion_compte` (`id`);

--
-- Contraintes pour la table `gestion_remboursement`
--
ALTER TABLE `gestion_remboursement`
  ADD CONSTRAINT `gestion_remboursement_agent_id_e78f9260_fk_gestion_agent_id` FOREIGN KEY (`agent_id`) REFERENCES `gestion_agent` (`id`),
  ADD CONSTRAINT `gestion_remboursement_credit_id_f0108c20_fk_gestion_credit_id` FOREIGN KEY (`credit_id`) REFERENCES `gestion_credit` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
