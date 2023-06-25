SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `bilibili_live_monitor_backup`
--

-- --------------------------------------------------------

--
-- 表的结构 `21987615-all-230623`
--

CREATE TABLE `21987615-all-230623` (
  `id` int(11) NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `mid` varchar(16) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` varchar(36) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_live` tinyint(1) NOT NULL DEFAULT '1',
  `cmd` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `danmaku` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `interact_num` tinyint(3) DEFAULT NULL,
  `gift_name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gift_price` int(11) DEFAULT NULL,
  `popularity` int(11) DEFAULT NULL,
  `info` varchar(6400) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='原神3.8前瞻';

--
-- 转储表的索引
--

--
-- 表的索引 `21987615-all-230623`
--
ALTER TABLE `21987615-all-230623`
  ADD PRIMARY KEY (`id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `21987615-all-230623`
--
ALTER TABLE `21987615-all-230623`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
