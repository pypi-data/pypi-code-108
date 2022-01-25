body {position:relative;z-index:1;/*background:url(bg.png)*/;background-color: #edf1f7;color: #333333; font: 13px  微软雅黑,Microsoft Yahei,Verdana, Arial, Helvetica, sans-serif; line-height: 1;
-webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
::selection { color: #fff; background: #fb6aa1; }
::-moz-selection {color:#fff;background:#fb6aa1;}
input::-ms-clear { display: none; }
a:link, a:visited { color: #444; text-decoration: none; -webkit-transition: background-color .15s linear, color .15s linear; -moz-transition: background-color .15s linear, color .15s linear; -o-transition: background-color .15s linear, color .15s linear; -ms-transition: background-color .15s linear, color .15s linear; transition: background-color .15s linear, color .15s linear; }
a:hover { color: #fd6ca3; }
.clear { clear: both; }
.box { background: #fff; /*border: solid 1px #d9dbdd; border-bottom-color:#dcdee0;*/border-radius:6px}
.boxx{border-radius: 5px 5px 0px 0px;}
h2 { font-size: 16px; /*font-weight: bold;首页文章不加粗*/ line-height: 1.5em; padding-bottom: 10px; }
h3 { font-size: 15px; line-height: 36px; height: 36px; }
.search_no{line-height: 30px;height: auto;font-size: 14px;padding:10px 5px;}
.search_no div{;text-align:center;font-size: 15px;margin: 30px auto;padding: 10px;border-radius: 5px;border: 1px solid #54aaff;color:#1e88e5 }
.search_no div a{color: deeppink}
.search_no span{color:red}
.container { max-width: 1180px; margin: 0 auto; }
strong { font-weight: bold; }
blockquote, pre { margin:40px 0 40px 0px;padding:0 20px 0 20px;border-left:1px solid #EEE;color:#AAA ;font-style:italic;line-height:24px}
blockquote p, pre p { text-indent: 0 !important }
center { margin: 0 auto; text-align: center }
.container_lod{}
/*header*/
.mainbar { background:#1b1b1b; /*border-bottom:1px solid #dfe5e9; */width:100%; height:40px;  }
#topbar { height: 40px; line-height: 40px; float: left; overflow: hidden; }
#topbar ul { list-style: none; }
#topbar ul li { height: 33px; line-height: 40px; float: left; padding: 0 50px 0 0; text-align: center; font-size:12px }
#topbar ul li a{ color:#565656}
#topbar ul li a:hover{ color:#fd6ca3}
#topbar ul ul { display: none; }
.toolbar { height: 30px; line-height: 30px; float: left; }
#rss { float: right; }
#rss ul li { margin: 10px 0 0 14px; float: right }
.icon1, .icon1 span.hover, .icon2, .icon2 span.hover, .icon3, .icon3 span.hover, .icon4, .icon4 span.hover, .icon5, .icon5 span.hover, .icon6, .icon6 span.hover { display: block; width: 24px; height: 24px; background: url(images/social_icon.gif) no-repeat; }
.icon1 { background-position: 0 -48px; }
.icon1 span.hover { background-position: 0 -72px; }
.icon2 { background-position: 0 -192px; }
.icon2 span.hover { background-position: 0 -216px; }
.icon3 { background-position: 0 -240px; }
.icon3 span.hover { background-position: 0 -264px; }
.icon4 { background-position: 0 -96px; }
.icon4 span.hover { background-position: 0 -120px; }
.icon5 { background-position: 0 -144px; }
.icon5 span.hover { background-position: 0 -168px; }
.icon6 { background-position: 0 0; }
.icon6 span.hover { background-position: 0 -24px; }
#blogname { outline: none; overflow: hidden; float:left; margin-top:1px; width:194px; }
#blogname h1 { text-indent: -9999px; height: 0; width: 0; }
#blognamess { outline: none; overflow: hidden; float:left; margin-top:15px; width:194px; }
#blognamess h1 { text-indent: -9999px; height: 0; width: 0; }
.search_phone { display: none }
/*loading*/
#main_loading{ position: fixed !important; position: absolute; top: 0; left: 0; height: 100px; width: 200px; z-index: 999; background: #000 url(images/loading.gif) no-repeat center; opacity: 0.6; filter: alpha(opacity=60); font-size: 14px; line-height: 20px; top: 50%; left: 50%; margin-top: -50px; margin-left: -100px; border-radius: 5px; }
#loading-one{ color: #fff; position: absolute; top: 50%; left: 50%; margin: 50px 0 0 -50px; padding: 3px 10px; }
#loading-one_m{
    olor: #fff;
    position: absolute;
    top: 50%; left: 50%;
    margin: 50px 0 0 -50px;
    padding: 3px 10px;}
#main_loading_m{
    position: absolute;
    margin-top: 200px;
    left: 50%;
    margin-left: -100px;
    height: 100px;
    width: 200px;
    z-index: 999;
    background: #000 url(images/loading.gif) no-repeat center;
    opacity: 0.6;
    filter: alpha(opacity=60);
    font-size: 14px;
    line-height: 20px;
    border-radius: 5px;
}


/*nav导航*/
.mainmenus { /*position:fixed;margin:0 auto; width:100%;*/
    /*background:url("images/navbg.png") repeat-x;*/
    background:#222222;position: relative;width: 100%;box-shadow:1px 2px 2px gray;
}
.home { float: left; height: 60px; width: 175px; background-image: url(images/logo.png) ; text-indent: -9999px;background-repeat: no-repeat;}/*顶部LOGO*/
.home_none { float: left; height: 60px; width: 175px; background-image: url(images/logo.png) ; text-indent: -9999px; background-repeat: no-repeat;}/*顶部LOGO*/
.home_none:hover { background-image: url(images/logo2.png)  }
.topnav { height: 60px;  font-size: 17px; /*font-weight: bold; */text-align: center; position:relative;text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.4); margin-left:-30px;}
.topnav a { color: #989898; height: 60px; font-size:16px;line-height: 60px;  }/*导航文字样式*/
.topnav a:hover  { color: #ef5b9c;}
.topnav ul { z-index: 999; }
.topnav li { height: 60px;line-height: 60px; float: left; position: relative; width: auto; transition: all 0.1s;box-sizing: border-box;}
.topnav li a:link, .topnav li a:visited { float: left; position: relative; display: block;padding:0 15px}
.topnav li a:hover, .topnav .current_page_item ,.topnav .current-menu-item,.topnav .current-post-parent{ /*background: #34495e;导航菜单颜色*/ float: left; position: relative; }
.topnav .color a{color: #ff4500}
.topnav .menu-item-has-children:after{position: absolute;right: 3px;top:28px;display: inline-block;content: '';width: 0;height: 0;border: 4px solid transparent;border-top:4px solid #ccc}
.topnav .menu-item-has-children .menu-children-ico{display: none}
.topnav ul ul {display:none;opacity:0;background-color: #333333;width: 800px;position: absolute; top: 57px; z-index: 999; left: 0; padding: 5px;margin: 0;}
.topnav ul ul:before{position: absolute;content: '';border: 8px solid transparent;border-bottom: 8px solid #333333;top:-16px;left: 40px;}
.topnav ul ul li { font-size: 13px; color: #363636; display: inline-block; position: relative; height: 35px; line-height: 35px; }
.topnav ul ul li a{transition: all 0.3s}
.topnav ul ul li a:link, .topnav ul ul li a:visited { padding:0;margin:0 3px;text-align: center;padding-top: 0;font-size: 14px; color: #ccc; display: inline-block; position: relative; width: 80px; height: 36px; line-height: 36px;   font-weight: normal; }
.topnav ul ul li a:hover { color: #ef5b9c;position: relative; font-weight: normal; }
.topnav ul ul ul { display: none; position: absolute; top: -1px; left: 190px; z-index: 999; }/*cuowu*/
.topnav ul ul ul li { font-size: 13px; color: #363636; display: block; position: relative; height: 36px; line-height: 36px; text-align: center; }
.topnav ul ul ul li a:link, .topnav ul ul ul li a:visited { font-size: 13px; color: #fff; display: block; position: relative; width: 150px; height: 36px; line-height: 36px; text-align: left; background: #363636; font-weight: normal; }
.topnav ul ul ul li a:hover { font-size: 13px; color: #fff; display: block; position: relative; width: 150px; height: 36px; line-height: 36px; text-align: left; background: #fd6ca3; font-weight: normal; }
.topnav .menu-button {display:none; position: absolute; top:8px; right:54px; cursor: pointer; }
.topnav .menu-button.active{background:rgba(0,0,0,0.2); border-radius:5px;}
.topnav .menu-button i{ display:block; width:100%; height:33px; background:url(images/icon.png) no-repeat -2px -236px;}
.menu-ico_span{color: #cccccc;float:right;background: none;height: 33px;line-height: 33px;}
.topnav .menu-right{ position:absolute; right:0; top:0}
.topnav .menu-right .menu-search{ position:relative;}
.topnav .menu-right #menu-search{ margin-top:8px; height:40px;width:14px;background: url(images/icon.png) no-repeat 5px -193px;}
.topnav .menu-right .menu-search .menu-search-form{ width: 200px; display:none; position:absolute; top:60px; right:0; background:#2c3e50; padding:15px; z-index:900}
.topnav .menu-right .menu-search .menu-search-form .button{border: none; background:#363636; color: #fff; padding: 6px 12px;}
.topnav .menu-right .current_page_item .menu-search-form{ display:block}
.topnav .menu-children-ico{ position: absolute;top:25px;right: 0px;color: #989898}
.subsidiary {height: 60px; padding: 0 10px; background:#fff; }
.bulletin { overflow: hidden; height: 40px; margin: 10px 0; line-height: 40px; ; border-radius: 5px; width:50%; background: url(images/gg.png) no-repeat #ffedc7 11px 11px; }
.sixth{ color: #999999;}
.sixth a{ color: #999999;}
.sywzad {float:left; height: 40px; line-height: 60px; width:25%;}
.sywzad a{ font-size:14px ; padding:0px 15px; color:#34495e;}
.sywzad a:hover{color:#3498db;}
.bdsharebuttonbox{ padding-top:10px; padding-left:-50px; float: left;}
.ggbaidu{ padding-top:5px; padding-left:-50px;float: right;}
.bulletin span { width: 70px; padding-left:10px; color:#6b3612;}
.bulletin marquee { color: #6b3612; }
.bdshare_small { margin-top: 10px; }
.triangle-down {  width: 0;  height: 0;border-left: 5px solid transparent;border-right: 5px solid transparent; border-top: 5px solid #a4a1a1;  display: inline-block;margin:0 0 0 5px;position: relative;  top:-2px;}
#mgssd_tips{text-align: center;font-size: 15px;color: #666;}


/*****************面包屑*******************/
.subsidiarys { background: #fff; height: 34px;}
.bulletins { overflow: hidden; height: 24px; margin: 5px 0; line-height: 24px; }
.bulletins span { width: 70px; }
.bulletins marquee { color: #999999; }
.bulletins a{ color: #999999; }
.bulletins { color: #999999; font-size:12px; }
.bdshares_small { margin-top: 5px; }

/*************************侧边栏***********************/
#sidebar { width: 280px; margin-left: 16px; float: right;}
#sidebar-follow { width: 316px; }
.widget { padding: 10px; }
.widget h3 { padding: 0; margin-bottom: 10px; height: 40px; line-height: 30px; border-bottom: #eff2f5  solid 1px; /*侧边栏*/font-size: 15px; font-weight: bold; color:#444}
.widget span { color: #fd6ca3; }
.widget em { color: #666; font-style: normal; margin-right: 20px; float: right; }
.widget ul { padding: 1px 0 1px 0; }
.widget ul li { line-height: 1.5em; border-bottom: dashed 1px #eff2f5 ; padding: 5px 0 }
.blogroll li { display: inline-block; margin-right: 10px }
/*文本*/
.textwidget { margin: -3px; overflow: hidden; width: 300px; }
.textwidget img { max-width: 300px; height: auto ;transition: all 0.4s}
.textwidget img:hover{opacity: 0.8}

.inter-top .textwidget { margin:0; overflow: hidden; width: auto; }
.inter-top .textwidget img { max-width: inherit; height: auto }
/*文章tab*/
#wzbt{position: relative;font-size: 20px;font-size: 2.0rem;line-height: 35px;text-align: center;padding: 7px 10px;font-weight: bold}
#tabnav { display: block; clear: both; zoom: 1; }
#tabnav li { float: left; width: 85px; border-bottom: #eff2f5  solid 1px; /*文章侧边框下线*/text-align: center; cursor: pointer; list-style: none; font-weight: bold; font-size: 15px; padding-bottom: 5px; margin-bottom: 5px; }
#tabnav .selected { position: relative; background-color: #fff; color: #fd6ca3; cursor: default; border-bottom: #eff2f5  solid 1px; }
#tab-content .hide { display: none; }
#tab-content ul { overflow: hidden; list-style: none }
#tab-content ul li { float: left; width: 100%; border-bottom: dashed 1px #eff2f5 ; background: url(images/zt_con_li.png) no-repeat left 12px;text-indent: 0.8em; }
#tab-content ul li a { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block }
/*评论*/
.r_comment { position: relative; overflow: hidden; height: auto; }
.r_comment ul { list-style: none; overflow: hidden; position: relative; }
.r_comment li { line-height: 22px !important; clear: both; height: 48px; margin-bottom: 5px; overflow: hidden; border-bottom: dashed 1px #eff2f5 ; }
.r_comment li:hover { border-right: #eff2f5 solid 3px; background: #f8f8f8; }
.r_comment ul li img.avatar { height: 35px; width: 35px; float: left; margin: 4px 8px 0 0; background: #fff; border: 1px solid #ddd; border-radius: 5px; }
/*登录*/
#loginform p { line-height: 26px; margin-bottom: 5px; }
#loginform input.login { width: 140px; padding: 2px; color: #444; border: 1px solid #dfdfdf; box-shadow: inset 2px 3px 5px #eee; }
#loginform input.denglu { width: 70px; margin-top: 5px; height: 63px; color: #444; text-align: center; border: 1px solid #dfdfdf; font-size: 16px; }
#loginform input.denglu:hover { background: #fd6ca3; color: #fff; }
.loginl { float: left; margin: 5px 10px 5px 0; }
.loginl label { margin-right: 10px; }
#loginform label input[type="checkbox"]{ vertical-align:middle; margin-right:3px}
#loginform input:focus { border: 1px solid #ccc; }
.register { margin: 0 10px 0 50px; }
.v_avatar { margin: 5px; float: left; width: 64px; }
.v_avatar img { border-radius: 5px; }
.v_li li { list-style-type: none; float: left; width: 100px; padding: 5px; }
/*标签*/
.tagcloud { height: auto; overflow: hidden; }
.tagcloud a:link, tagclouda:visited { font-size:12px; color:#999;padding: 3px 8px;  border:solid 1px #cccccc; margin: 2px; height: 20px; line-height: 30px; -moz-border-radius: 3px; border-radius: 3px; white-space: nowrap; -webkit-transition: background-color .15s linear, color .15s linear; -moz-transition: background-color .15s linear, color .15s linear; -o-transition: background-color .15s linear, color .15s linear; -ms-transition: background-color .15s linear, color .15s linear; transition: background-color .15s linear, color .15s linear; }
.tagcloud a:hover {  color: #fd6ca3; border:solid 1px #fd6ca3; }
.action { border-top: solid 1px #F3F3F3; margin-top: 5px; padding-top: 5px; text-align: right; }
.action a { color: #CCCCCC; }
/*图文*/
.imglist{ /*margin-left:-10px*/}
.imglist li{ width:280px; /*margin-left:10px;border-bottom:none !important; padding:0 !important;*/min-height: 70px;}
.imglist li h4{width:170px;float:left; margin:10px 0 10px 15px;height:20px;white-space: nowrap;text-overflow:ellipsis; overflow:hidden;}
.imglist li img{ float:left;width:65px; height:60px}
.imgtimes {float:left; font-size:12px; line-height:12px; margin-left:15px; color:#999;}
.imgtimes span { color:#999999}
.imgtimes a{ color:#999;}
.imgss{float:left; margin-top:5px; margin-bottom:5px;}
.post h4 {color:#444}
.post h4:hover {color:#fd6ca3}


/*日历*/
#wp-calendar{width: 100%;border-collapse: collapse;border-spacing: 0;  magrin:0 auto;       }
#wp-calendar #today{font-weight: 900; color: #990099 ;display:block;background-color: #F3F3F3; text-align:center;}
#wp-calendar thead{font-size:14px;}
#wp-calendar tfoot td{border-top:1px solid #F3F3F3;background-color:white; }
#wp-calendar tfoot td a{ color:#CCCCCC;}
#wp-calendar caption{font-size:15px;border-bottom: #eff2f5  solid 1px;padding:5px 0;margin-bottom:10px;}
#wp-calendar thead th{text-align:center;}
#wp-calendar tbody td{text-align:center;padding: 7px 0;}
#wp-calendar a {color: #990099; text-decoration: none; cursor:pointer;}
#wp-calendar a:hover {color:#fd6ca3 ; text-decoration:none;font-weight:900;}
/*首页文章列表*/
.mainleft { width: auto; overflow: hidden;margin-top: 50px;}
#post_container { margin-left: -16px; position:relative;}
#post_container li { display: block;width: 500px;margin-top:2px; width: 280px; margin-left: 18.5px; float: left; border: 1px solid #ccc; box-sizing: border-box; transition: all 0.2s; box-shadow:0px 2px  5px -3px gray; padding:2px;  }

/*

.post_hover { transition: all 0.3s  }

.post_hover:hover{ box-shadow:5px 5px 10px 1px gray;}

*/

#post_container li:hover{  box-shadow:0px 5px  6px -3px gray; position:relative; top:-1px; }

.thumbnail { max-height: 500px; overflow: hidden;  }
.thumbnail a { display: block; /*padding: 10px 10px 0 10px;*/ }
.thumbnail img {min-width: 280px; height: auto; }
.article { padding: 5px 10px 0px 10px;position:relative;}/*高度*/
.article h2{  line-height:1.5em; font-size:14px; font-weight:400;text-align: center;overflow: hidden}
.article h2 a{ color:#444444; }
.article h2 a:hover{ color:#fd6ca3;}
.info { margin-left:-2px;  margin-top:-10px; color: #9aabb8; margin-bottom:2px; /* white-space: nowrap;text-overflow: ellipsis; position: relative; border-top: 1px solid #DFDFDF; background: #F9F9F9; line-height: 25px; padding: 0 -2px;*/ /*text-align: center; */ }
.info span { height: 20px; line-height: 17px;font-size:12px;}
.info span a { color: #999999;  line-height:2em;}/*文章标题字颜色*/
.info span a:hover { color: #333333; }
.info_ico { background: url(images/info.png) no-repeat; padding: 0 5px 0 20px; }
.info_category { border-radius: 5px; /*background-color:#dfe5e9;*/ color:#9aabb8; padding:0px 0px 0px 5px; }
.info_categorys { border-radius: 5px; background-color:#dfe5e9; color:#9aabb8; padding:0px 5px 0px 5px; }
.info_date { background-position: 0 -1px; }
.info_views { background-position: 0 -62px; }
.info_comment { background-position: 0 -43px; }
.info_author { background-position: 0 -82px; }
.entry_post { line-height: 0px; color: #666; margin-bottom:0px; word-break: break-all; }
.entry_post  p{ padding-bottom:10px;}
.sticky { background: #fd6ca3; height: 25px; width: 45px; position: absolute; z-index: 20; top: -1px; right: -1px; color: #fff; font-weight: bold; text-align: center; line-height: 25px; }
.ssticky { font-size:14px;color:#FFF;padding-left:8px;height: 70px;width: 72px; line-height:2.8em;display: block;overflow: hidden;background-position: -314px 0;position: absolute;left:0;top:0;z-index: 10;}
.icons,.flex-direction-nav li a{background: url("./images/icons.png") no-repeat;}
.arrow-catpanel-top { position: absolute; /*background: url(images/arrow-catpanel-top.png) no-repeat 0px 0px;*/ width: 52px; height: 14px; bottom:-1px; left: 130px; z-index: 10; }
/*zoom { width: auto; height: auto; display: block; position: relative; overflow: hidden; background: none; }*/

/*.zoomOverlay { position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    display: none; !*margin: 10px 10px 0 10px;对应图像尺寸*!
    background-image: url(images/zoom.png);
    background-repeat: no-repeat;
    background-position: center;
    background-color:gba(247, 164, 164, 0.97) !important}*/
#post_container .fixed-hight h2 a{ /*display:block;*/white-space: nowrap;text-overflow:ellipsis; overflow:hidden;display: block;text-align: center}/*文章列表标题center无效因为这里有display*/
#post_container .fixed-hight .entry_post{overflow: hidden;height: 1px;}
#post_container .fixed-hight .info{ overflow:hidden; height:26px;}
#post_container .fixed-hight .thumbnail{height:159px; overflow: hidden;background:url("") no-repeat;background-size: cover;}

/*分页*/
.navigation.pagination a{transition: all 0.2s}
.pagination a,.pagination span { width: 40px; text-align: center; height: 40px; line-height: 40px; margin: 0px 0 0px 4px; display: inline-block; text-decoration: none; border-style:solid; border-width:1px; border-color:#ccc;color: #999; border-radius:3px;}
.pagination a.extend { padding: 0 5px;display: none; }
.pagination .current { height: 40px; width: 40px;color: #fd6ca3; border-style:solid; border-width:1px; border-color:#fd6ca3; margin: 20px 0 0 4px; margin-bottom:60px; }
.pagination a:hover { height: 40px; width: 40px; color: #fd6ca3; text-decoration: none; /*background: #348fca;*/ border-radius:3px;border-style:solid; border-width:1px; border-color:#fd6ca3;}
.pagination .page_previous, .pagination .prev { width: 80px; height: 40px; text-align: center; }
.pagination .page_previous:hover, .pagination .prev:hover { width: 80px; height: 40px; text-align: center; }
.pagination .page_next, .pagination .next, .pagination .page_next:hover, .pagination .next:hover { width: 80px; height: 40px; text-align: center; }
.pagination .fir_las, .pagination .fir_las:hover { width: 34px; height: 80px; text-align: center; }
/*single文章页面*/
.article_container { padding:30px;border: 1px solid #EEEEEE;box-shadow: 2px 2px 3px #EEE;position: relative}
.article_container h1 {/*文章页面对齐样式*/ color:#222222; margin-top:-10px; position: relative; font-size: 1.8em; line-height: 30px; text-align: center; padding: 7px 0; font-weight: bold;}
.article_info { text-align: left;/*文章页面对齐*/ margin-bottom:10px; line-height: 1.5em; color:#9aabb8;/*文章页文字颜色*/ font-size:12px; }
.xian { margin-left:-15px;  margin-right:-15px;border-bottom:#eff2f5 solid 1px;/*文章页标题下划线*/ margin-bottom:15px; line-height: 1.5em; color:#999;/*文章页文字颜色*/  }
.article_info a { color: #9aabb8 }
.article_info a:hover { text-decoration: underline;color: #9aabb8 }
.context { overflow: hidden; }
#post_content{ padding:10px 0px}/*缩近*/
#post_content a{ /*text-decoration:underline*/}
.context, .context p, .context pre { line-height: 2em; font-size: 14px;}
.context a{ color:#fd6ca3;font-size: 14px;line-height: 2em; }
.context ol, .context ul { margin-left: 40px; }
.context ol li, .context ul li { line-height: 2em; }
.context ol li { list-style-type: decimal; }
.context ul li { list-style: url(images/zt_con_li.png);}
.context h3,.context h4,.context h5{/*border-bottom:#dedede 1px solid;*/padding-bottom:2px;margin-bottom:10px;font-weight:bold;font-size:20px;padding-top:5px;}
.context h1{font-size:28px;font-weight:bold;}
.context .other{padding:10px 0;margin-bottom:15px;color: #555;font-size:18px;margin:15px 0;border-bottom: 1px solid #eaeaea;font-family: 微软雅黑,Microsoft Yahei,Verdana, Arial, Helvetica, sans-serif;font-weight:800;}
.context p embed, .context object { margin: 0 auto }
.context code { background: #FFF8DF; color: #9C2E0E; font-style: italic; padding: 2px 3px; line-height: 2em; }
.context table{border-top:solid 1px #ddd;border-left:solid 1px #ddd;width:100%;margin-bottom:16px}
.context table th{background-color:#f9f9f9;text-align:center}
.context table td,.article-content table th{border-bottom:solid 1px #ddd;border-right:solid 1px #ddd;padding:5px 10px}
.context .alignleft{float:left;text-align:left;margin-right:10px}
.context .aligncenter{text-align: center;display:block;margin:auto;}
.context .alignright{float:right;text-align:right;margin-left:10px}
.context .wp-caption {border: solid 1px #eee;border-radius: 2px;padding:5px;box-shadow: 2px 2px 0 #fbfbfb;margin-bottom: 15px; max-width:100%;}
.context .wp-caption:hover {border-color: #ddd;}
.context .wp-caption-text {margin:  5px -5px -5px;border-radius: 0 0 2px 2px;background-color: #fbfbfb;border-top: 1px solid #eee;padding: 5px;color: #999;}
.context .article_tags { font-size: 12px; line-height: 40px; margin-top: 15px; text-align: center; border-top: 1px #cdcdcd dashed; border-bottom: 1px #cdcdcd dashed; }
.context .img-responsive{display:block;height:auto;max-width:100%}
.baishare {  margin: 8px 0 0 0; _margin: 5px 14px 0 0; }
#authorarea { position: relative; float: left; padding:10px; line-height:20px; }
#authorarea{ width:300px;  float:left;}
#authorarea ul{ width:880px; }
#authorarea li{ width:270px; float:left; display:block;overflow:hidden; padding-right:10px;}
#authorarea li a { line-height:25px; display:block; word-break:keep-all; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.author_arrow { position: absolute; float: left; border-style: solid; border-width: 10px; /*border-color: transparent #fff transparent transparent;*/ height: 0; width: 0; font-size: 0; top: 42px; left: 80px; }
.authorinfo { height: 80px; padding-left: 110px; }
.post-navigation { clear: both; overflow: hidden;  }
.post-navigation div { display: block; position: relative; font-size: 14px; color: #999; }
.post-next { float: right; text-align: right; padding-right: 30px; }
.post-previous { float: left; padding-left: 30px; }
.post-navigation div a:after { position: absolute; color: #CCC; font-size: 36px; margin-top: -11px; height: 22px; line-height: 22px; top: 34%; }
.post-previous a:after { content: '«'; left: 0px; }
.post-next a:after { content: '»'; right: 0px; }
/*相关文章*/
.articlecc { padding: 5px 10px 0px 10px;position:relative;height: 20px;
}/*高度*/
.articlecc h2{  line-height:1.5em; font-size:14px; font-weight:600; overflow: hidden;
}
.articlecc h2 a{ color:#444444; width:250px;display:block; word-break:keep-all; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
.articlecc h2 a:hover{ color:#fd6ca3;}
.thumbnailcc {height: 150px; overflow: hidden; }
.thumbnailcc a { display: block; /*padding: 10px 10px 0 10px;*/ }
.thumbnailcc img {width: 100%;height: auto;transition: all 0.3s}
.related { float:left; }
.related ul { width:950px;  }
.related ul li{ width:280px; float:left; margin-right:20px;overflow: hidden;}
.related ul li:hover img{opacity: 0.8}
.related_box { float: left; width: 280px; height: 285px;}
.related_box:hover { background-color:#f0f2f7;  }/*颜色*/
.related_box a:hover {color:#779ed4 }
.related_box .r_title { padding: 0 8px; text-align: center; }
.related_box .r_pic { margin: 8px auto; width: 140px; height: 94px;}
.related_box .r_pic img { width: 140px; height: 94px; }
#content table, #content button { margin: 10px auto; }
#content p { margin: 0 0 20px 0 }
#content hr { background: url(images/sprite-2.png) no-repeat -1px -93px; height: 3px; border: none; margin: 15px 0 }
#content .content_post ol li { list-style: decimal inside; color: #272727; line-height: 26px; font-size: 13px }
#content .content_post ul li { background: url(images/li.png) no-repeat; text-indent: 1.3em; color: #272727; line-height: 26px; font-size: 13px }
#content b, #content strong { font-weight: blod }
#content i, #content em, #content var, #content dfn { font-style: italic }
#content th, #content td { display: table-cell; vertical-align: inherit; padding: 1px; line-height: 2em }
#content th { font-weight: 700; padding: 1px }
#content td { text-align: inherit; padding: 1px }
#content .pagelist { padding: 10px 0; background: #f3f3f3; text-align: center; margin-top: 20px ;}
#content .pagelist>span,#content .pagelist>a{background-color: #fff ;/*border: 1px#ddd solid ;*/color: #99a1a7;margin-left: 5px;padding: 4px 10px ;text-transform: uppercase; border-radius:3px}
#content .pagelist>a:hover,#content .pagelist>span{background-color: #348fca;color: #fff !important;}
#content .pagelist a { margin-right: 10px }
.alignleft { float: left; margin: 5px 15px 5px 0 }
.alignright { float: right; margin: 5px 0 5px 15px }
/*comments*/
#comments { font-size: 15px; font-weight: bold; margin-left: 10px; height:auto; padding-top: 20px;  }
#comments_box .navigation{ margin-right:10px; font-size:12px}
#comments_box .pagination a,#comments_box .pagination span,#comments_box .pagination .current{ line-height:20px; height:20px}
#respond_box {  font:  微软雅黑,Microsoft Yahei,Verdana, Arial, Helvetica, sans-serif; }
#respond { margin: 10px 10px 20px 10px; border-top: 1px solid #dedede; padding-top: 10px; }/*评论线*/
#respond p { line-height: 30px; text-align: right; }
#respond h3 { font-size: 16px; font-weight: bold; line-height: 25px; height: 25px; }
.comt-box { border: solid 1px #DDD; border-color: #C6C6C6 #CCC #CCC #C6C6C6; border-radius: 3px; padding: 8px; box-shadow: inset 2px 0 2px #F2F2F2, inset 0 2px 2px #EEE, 0 2px 0 #F8F8F8, 2px 0 0 #F8F8F8; background-color: white; clear: right; }
.comt-area { _margin-top: -35px; border: 0; background: none; width: 100%; font-size: 12px; color: #666; margin-bottom: 5px; min-height: 70px; box-shadow: none; }
.comt-ctrl { position: relative; margin: 0 -8px -8px; _margin-right: -10px; height: 32px; line-height: 32px; border-radius: 0 0 3px 3px; border-top: solid 1px #DDD; background-color: #FBFBFB; box-shadow: inset 0 1px 0 #FBFBFB; color: #999; }
.comt-submit { position: absolute; right: -1px; top: -1px; border: solid 1px #CCC; height: 34px; width: 120px; cursor: pointer; font-weight: bold; color: #666; font-size: 12px; border-radius: 0 0 3px 0; background-image: -webkit-linear-gradient(#F6F6F6, #E2E2E2); text-shadow: 0 -1px 0 white; }
#comment-author-info { margin-bottom: 10px; height: 27px; }
#comment-author-info label { margin-left: 5px; }
#comment-author-info input { width: 20.5%; margin-left: -4px; margin-top: -5px \9; vertical-align: middle \9; }
.comment_input { margin-left: 27px; }
#real-avatar { float: left; width: 27px; }
#real-avatar img { width: 27px; height: 27px; }
.comt-addsmilies, .comt-addcode { float: left; color: #888; padding: 0 10px; }
.comt-smilies { display: none; position: absolute; top: 0; left: 40px; height: 30px; background-color: #FBFBFB; overflow: hidden; }
.comt-smilies a { float: left; padding: 8px 1px 0px; }
.comt-num { font-size: 12px; color: #999; float: right; margin-right: 140px; }
.comt-num em { font-weight: bold; font-size: 14px; }
.commentlist .comment { list-style: none; border-top: 1px solid #ddd; }
.commentlist li.comment ul.children { margin-left: 20px; }
.commentlist .depth-1 { margin: 0; }
.commentlist li { position: relative; }
.commentlist .thread-even { background: #fafafa; }
.commentlist .comment-body { padding: 10px; border-left: 5px solid transparent; }
.commentlist .comment-body:hover { background: #f5f5f5; border-left: 5px solid #fd6ca3; }
.commentlist .comment-body p { margin: 5px 0 5px 50px; line-height: 22px; }
.reply a:link, .reply a:visited { text-align: center; font-size: 12px; }
.datetime { font-size: 12px; color: #aaa; text-shadow: 0px 1px 0px #fff; margin-left: 50px; }
.commentmetadata { font-size: 12px; color: #aaa; text-shadow: 0px 1px 0px #fff; margin-left: 50px; }
ol.commentlist li div.vcard img.avatar { width: 40px; height: 40px; position: relative; float: left; margin: 4px 10px 0 0; border-radius: 5px; }
ol.commentlist li div.floor { float: right; color: #bbb }
.children li.comment-author-admin { border-top: #dedede solid 1px; }
/*footer*/
#footnav a, #friendlink a { color: #666666; font-size:10px; }
#footnav a:hover, #friendlink a:hover { color: #fd6ca3}
#footer { text-align: center; background: #1a1a1a; padding: 20px 0 15px 0; font-size: 12px; color: #666666; line-height: 1.5em; box-shadow: 0px -2px 3px gray;margin-top: 30px;}
#footer p { text-align: center; }
.footnav { line-height: 30px; font-size: 12px; }
.footnav ul { list-style: none; text-align: center; }
.footnav ul li { height: 30px; line-height: 30px; display: inline; padding: 0 10px 0 0; }
.footnav ul ul { display: none; }
.copyright { color: #666666;font-size:12px;}
.copyright p{ line-height:2em }
.copyright a { color: #666666; font-size:12px;}
.copyright a:hover { color: #fd6ca3; }
#footer p.author a { color: #666666; }
#footer p.author a:hover { text-decoration: underline }
#footer .footer_about p span{color: orangered}
#footer .footer_about p span:after{content: '友链及广告合作请联系QQ：'}

/*gototop*/
#tbox { width:45px; float: right; position: fixed; right: 20px; bottom: 150px; }
#pinglun, #home, #gotop { width:45px; height:45px; background: #fd6ca3 url(images/icon.png) no-repeat; display: block; margin-bottom: 5px; filter: alpha(Opacity=50); -moz-opacity: 0.5; opacity: 0.5; }
#pinglun:hover, #home:hover, #gotop:hover { filter: alpha(Opacity=100); -moz-opacity: 1; opacity: 1; }
#pinglun { background-position: 0 -50px;display: none }
#home { background-position: 0 5px; }
#gotop { background-position: 0 -100px; }
/*幻灯*/
/*.slider {!* border:10px solid #FFF;width: 648px;*! overflow: hidden; padding-top:10px;}!*边框*!
#focus { width: 100%; height: 370px; overflow: hidden; position: relative; }
#focus ul { height: 430px; position: absolute; }
#focus ul li { float: left; width: 648px; height: 370px; overflow: hidden; position: relative; background: #ccc; }
#focus ul li div { position: absolute; overflow: hidden; }
#focus .button { position: absolute; width: 648px; height: 10px; padding: 5px 10px; right: 0; bottom: 0; text-align: right; }
#focus .button span { display: inline-block; _display: inline; _zoom: 1; width: 25px; height: 10px; _font-size: 0; margin-left: 5px; cursor: pointer; background: #fff; }
#focus .button span.on { background: #fff; }
#focus .preNext { width: 45px; height: 100px; position: absolute; top: 125px; background: url(images/sprite.png) no-repeat 0 0; cursor: pointer; }
#focus .pre { left: 0; }
#focus .next { right: 0; background-position: right top; }
#focus ul li a { display: block; overflow: hidden; }
#focus ul li a img { width: 650px; height: auto; }
.flex-caption { float:right;  background: #fff; border:10px solid #FFF;opacity: 0.8; color: #fff; height: 430px;padding: -20px -40px;}
.flex-caption a { color: #999; }
.flex-caption:hover { opacity: 1; }
.flex-caption .btn { display: none; }
.slides_entry { display: none; }
!*读者墙*!*/
/*.readers-list { line-height: 19px !important; text-align: left; overflow: hidden; _zoom: 1;}
.readers-list li { width: 200px; float: left; *margin-right:-1px}
.readers-list a, .readers-list a:hover strong { background-color: #f2f2f2; background-image: -webkit-linear-gradient(#f8f8f8, #f2f2f2); background-image: -moz-linear-gradient(#f8f8f8, #f2f2f2); background-image: linear-gradient(#f8f8f8, #f2f2f2) }
.readers-list a { font-size:12px;  line-height:19px !important; position: relative; display: block; height: 36px; margin: 4px; padding: 4px 4px 4px 44px; color: #999; overflow: hidden; border: #ccc 1px solid; border-radius: 2px; box-shadow: #eee 0 0 2px }
.readers-list img, .readers-list em, .readers-list strong { -webkit-transition: all .2s ease-out; -moz-transition: all .2s ease-out; transition: all .2s ease-out }
.readers-list img { width: 36px; height: 36px; float: left; margin: 0 8px 0 -40px; border-radius: 2px }
.readers-list em { color: #666; font-style: normal; margin-right: 10px }
.readers-list strong { color: #ddd; width: 40px; text-align: right; position: absolute; right: 6px; top: 4px; font: bold 14px/16px microsoft yahei }
.readers-list a:hover { border-color: #bbb; box-shadow: #ccc 0 0 2px; background-color: #fff; background-image: none }
.readers-list a:hover img { opacity: .6; margin-left: 0 }
.readers-list a:hover em { color: #fd6ca3; font: bold 12px/36px microsoft yahei }
.readers-list a:hover strong { color: #fd6ca3; right: 150px; top: 0; text-align: center; border-right: #ccc 1px solid; height: 44px; line-height: 40px }
.readers-list span.name{word-break:break-all; max-width:120px; display:block}*/
/*文章归档*/
.articles_all { line-height: 35px; padding-left: 15px; border-top: #dedede solid 1px }
.car-container { padding: 0 15px 10px 15px; }
.car-collapse .car-yearmonth { cursor: s-resize; }
a.car-toggler { line-height: 30px; font-size: 14px; color: #c30 }
.car-list li { list-style: none; line-height: 24px }
.car-list li ul { padding-left: 30px }
.car-plus, .car-minus { width: 15px; display: block; float: left; font-family: Courier New, Lucida Console, MS Gothic, MS Mincho; }
.car-monthlisting span { color: #ccc; }
.new { float: left;; margin-top:5px;}

/*友情链接*/
.flink, .linkstandard { list-style: none; }
.flink ul ul, .linkstandard ul { padding: 0 15px 10px 15px; list-style: none; line-height: 24px; }
.flink ul ul li { float: left; height: 30px; width: 25%; overflow: hidden; line-height: 30px; }
.flink ul li h2, .linkstandard h2 { clear: both; font-size: 16px }
/*页面*/
.cont_none ul, .cont_none ul li { list-style: none; margin: 0; }
/**/
.toppostbox{ margin-right:6px; float: right;/*border:10px solid #FFF;*/ width:315px;height:370px;position:relative;overflow:hidden; }
.toppostbox li{float:right;width:330px;height:55px;margin-bottom: 1px ;padding:9px;background:/*#f5f5f5*/#FFF;/*padding:8px 0px 10px 180px; margin: 0px -15px 1px 0px;*/}
.toppostbox img{float:left;width:86px;height:55px;position:relative;}
.toppostinfo{float:left;width:164px;height:55px;padding-left:40px;line-height:18px;position:relative;}/*随机文字位置*/
.topposttitle{width:164px;white-space:nowrap;overflow:hidden;-o-text-overflow:ellipsis;text-overflow:ellipsis;}
.topposttitle a{font-size:14px;line-height:1.5;}
.topposttitle a:hover{color:#fd6ca3;}
.toppostdate{float:right;width:164px;font-size:12px;color:#999;line-height:1.5;}
.sysjt {float:right;margin-right:10px; }/*随机图片位置*/
/*资讯列表*/
.spost_list{margin-bottom:00px;padding:10px 30px 10px 15px;background-color:#FFF;/*box-shadow:0 1px 2px #CCC;*/overflow:hidden; border-bottom:#eff2f5 solid 1px;white-space: nowrap;text-overflow:ellipsis; overflow:hidden; }
.spost_list:hover{ /*box-shadow: #b8c4d1 0px 0px 5px;*/ background-color:#f9f9f9; }
.spost_list h2{padding:10px 10px 10px 0px; overflow:hidden;text-overflow:ellipsis}
.spost_list h2 a{color:#444444;font-size:18px;overflow:hidden;white-space:nowrap}
.spost_list h2 a:hover{color:#fd6ca3;text-decoration:none}
.sexcerpt{margin-top:10px;line-height:18px; color:#444;}
.sexcerpt h2{padding:10px 10px 10px 0px; overflow:hidden;text-overflow:ellipsis}
.sexcerpt h2 a{color:#444444;font-size:18px;overflow:hidden;white-space:nowrap; font-weight:600; }
.sexcerpt h2 a:hover{color:#fd6ca3;text-decoration:none}
.sexcerpt p{ line-height:25px; color:#999}
.smore{padding-left:20px}
.smeta{font-size:12px;clear:both;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;color:#999;border-top:1px solid #EEE;margin:20px -30px 0 -30px;padding:10px 30px 0 30px}
.smeat_span{margin-right:15px}
.smeta a{color:#444}
.smeta a:hover{color:#444;text-decoration:underline}
.sthumbnail{float:left;padding:4px;/*border-radius:3px;border:1px solid #ccc;background:#f9f9f9;box-shadow:1px 1px 2px #d3d3d3;*/margin:0 15px 15px 0;}
.sthumbnail img{display:block;width:236px;height:150px;border-radius:5px;}

.smore{padding-left:20px;}
.2thumbnail { max-height: 500px; overflow: hidden;}
.2thumbnail a { display: block; /*padding: 10px 10px 0 10px;*/ }
.2thumbnail img { width: 330px; height: auto; }
.2zoom { width: auto; height: auto; display: block; position: relative; overflow: hidden; background: none; }
.2zoomOverlay { position: absolute; top: 0; left: 0; bottom: 0; right: 0; display: none; /*margin: 10px 10px 0 10px;对应图像尺寸*/ background-image: url(images/zoom.png); background-repeat: no-repeat; background-position: center;}
.sinfo { padding:0px 0px 5px 15px; color: #999;   /* white-space: nowrap;text-overflow: ellipsis; position: relative; border-top: 1px solid #DFDFDF; background: #F9F9F9; line-height: 25px; padding: 0 -2px;*/ /*text-align: center; */}
.sinfo span { height: 20px; line-height: 17px; font-size: 12px; color:#9aabb8;margin-left:-5px; }
.sinfo span a {  line-height:2;  color: #999;  }
.sinfo span a:hover { color: #9aabb8; }
.sinfo_ico { background: url(images/info.png) no-repeat; padding: 0 5px 0 20px; }
.sinfo_date { background-position: 0 -1px; }
.sinfo_views { background-position: 0 -62px; }
.sinfo_comment { background-position: 0 -43px; }
.sinfo_author { background-position: 0 -82px; }
.syad {width:auto 0; padding:40px 0px 5px 0px;text-align:center;margin-left:auto; margin-right:auto; background-color:#141414;}
.syads {width:auto 0; padding:0px 0px 5px 0px;text-align:center;margin-left:auto; margin-right:auto;}

/*文字广告*/
.bannerx{margin-bottom:10px;padding:10px 15px;border:solid 1px #bce8f1;border-radius:5px;background:#d9edf7;color:#31708f;font-size:14px; margin:10px 0px;}/*蓝*/
.banner{margin-bottom:5px;padding:5px 15px;border:solid 1px #faebcc;border-radius:5px;background:#fcf8e3;color:#a66d3b;font-size:14px; margin-top:30px;}/*黄*/
.banner lan{margin-bottom:10px;padding:10px 15px;border:solid 1px #d6e9c6;border-radius:5px;background:#dff0d8;color:#3c763d;font-size:14px}/*绿*/
.banner lan{margin-bottom:10px;padding:10px 15px;border:solid 1px #ebccd1;border-radius:5px;background:#f2dede;color:#a94442;font-size:14px}/*红*/
.banner a { font-weight:bold; color:#F00}
#blognamess{ display: none  }
.left { float:left}
.indexPart2Right ul li{ list-style-type: decimal; }
.indexPart2Right { border-radius:5px; width:260px;height:auto;padding:20px 10px 20px 10px; margin-left:20px;white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.indexPart2Right:hover { }
.indexPart2Right li { width:260px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:5px; _margin-top:14px;}
.indexPart2Right li a {white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:260px; color:#666;  font-size:12px;}
.indexPart2Right li a:hover { color:#fd6ca3; }
.indexPart2Right li span {
    display:inline-block;
    margin-right:8px;
    background:#ff6100;
    width:22px;
    text-align:center;
    color:#fff;
    transition:all .5s ease-out;
    -webkit-transition:all .5s ease-out;
    -moz-transition:all .5s ease-out;
    -o-transition:all .5s ease-out;
    -ms-transition:all .5s ease-out
}
.indexPart2Right li:hover span {
    transform:rotate(360deg);
    -webkit-transform:rotate(360deg);
    -ms-transform:rotate(360deg);
    -moz-transform:rotate(360deg)
}
.indexPart2Right h3 {
    font:bold 14px/normal 'MicroSoft Yahei';
    color:#ddd;

    width:260px;
}
.indexPart2Right h3 span a {
    float:right;
    font-size:12px;
    color:#666;
    background-color:#222222;
    padding:0 5px;
    border-radius:3px;
}
.indexPart2Right h3 span a:hover {
    float:right;
    font-size:12px;
    color:#fff;
    background-color:#fd6ca3;
    padding:0 5px;
    border-radius:3px;
}
.fens{
    background-color:#141414;

    padding-top:20px;
    padding-bottom:20px;
}
/*new jia*/
#container {
    margin:0 auto;
    padding:0px 0px 10px 0
}
#content .single-container {
    width:1200px;
    margin:20px 0 40px 0;
    padding:40px;
    height:auto
}
#content .review {

    margin-top:20px;
    padding:0px
}
.archive-header-info {
    text-shadow:0 1px 0 #FFF;
    color:#333
}
.archive-header-info {
    width:70%;
    margin-right:0
}
.archive-description {
    font-size:15px;
    line-height:18px;
    font-weight:300
}
.archive-description a {
    color:#fd6ca3;
    font-weight:600
}
.archive-description {
    color:#777
}
.archive-description {
    margin-bottom:40px
}
.header-logo a, .archive-title, .archive-title h1, .review .review-title h1, .similar-title, .single-title, .single-container h1, .single-container h2, .single-container h3, .footer-column h3, .footer-promo-title, .thumb .thumb-info .thumb-title .thumb-name h2, #header-bottom-left ul li a, .notice, .dashboard-section {
    font-weight:700;
    letter-spacing:-1px
}
.archive-title {
    font-size:30px;
    line-height:32px
}
.archive-title h1 {
    font-size:32px;
    line-height:32px
}
.archive-title {
    padding-top:15px;
    margin-bottom:10px
}
.archive-header-info {
    float:left;
    width:840px;
    margin-right:55px
}
.archive-header-ad {
    float:left;
    width:280px
}
.review-cats{color:#AAA; margin-top:20px; }
.review-cats a
{line-height:3em;
    -webkit-border-radius:4px;
    -moz-border-radius:4px;
    border-radius:4px
}
.review-cats a {
    font-weight:300
}
.review-cats a {
    color:#AAA;
    border:1px solid #ccc;
    text-transform:capitalize
}
.review-cats a:hover {
    color:#FD6CA3;
    border:1px solid #FD6CA3
}
.review-cats {
    line-height:30px;
    margin-bottom:20px
}
.review-cats strong
{color:#666666;
    font-weight:normal;
    display:block;
    font-size:8px;
    text-transform:uppercase;
    line-height:10px;
    margin-bottom:10px
}

.review-cats a {
    height:30px;
    padding:4px 9px;
    text-decoration:none;
    margin:0 5px 30px 0 !important;
    white-space:nowrap;
    background:none
}
/**/
.floating-pagi a {
    z-index:1000
}
.floating-pagi a {
    display:block;
    position:fixed;
    top:50%;
    width:60px;
    height:60px;
    outline:none
}
.floating-pagi .floating-pagi-next a {
    left:30px;
    -webkit-transform:rotate(-180deg);
    -moz-transform:rotate(-180deg);
    -ms-transform:rotate(-180deg);
    -o-transform:rotate(-180deg);
    filter:progid:DXImageTransform.Microsoft.BasicImage(rotation=3)
}
.floating-pagi .floating-pagi-prev a {

    right:30px
}
.floating-pagi svg {
    width:60px;
    height:60px
}
.floating-pagi svg {
    fill:#999
}
.floating-pagi:hover svg {
    fill:#FD6CA3
}
.floating-pagi a:hover {
    border:none;
    text-decoration:none
}
/*PCsearch*/
#header-bottom-right {display: none; width:170px; margin:0; padding:8px 15px;position: absolute; right: 0; top:60px; background-color: #313030;}
#header-bottom-right .search { width: 100%;  border: 1px solid gray; }
#header-bottom-right .search-field-holder { width: 100%;}
#header-bottom-right .search-field-holder .search-field { display: inline-block; width: 130px; padding: 5px 0; height: 18px; text-indent: 5px; background:#fbfafa;transition: all 0.2s; }
#header-bottom-right .search-field-holder .sousuo{ width: 32px;height: 32px; background: url("images/search-bottom.png") no-repeat;  float: right;  display: inline-block; border: none; }
#header-bottom-right .search-field-holder .search-field:hover{ background: #fff}
#header-bottom-right .search-field-holder .sousuo:hover{opacity: 0.8}
.search-button-top{position: absolute;right: 0;top:50%;margin-top: -15px;z-index: 99999}
.search-button-top button{height: 32px;width: 32px;background: url("images/search-top.png") no-repeat;border: none;opacity: 0.7;transition: all 0.2s;}
.search-button-top button:hover{opacity: 1}

.header-search {
    clear:both;
    float:none;
    width:360px;
    display:block;
    position:absolute;
    top:50px;
    margin-left:20px;
    z-index:10000;
    border-bottom:1px solid #000;
    box-shadow:0 1px 0 #222;
    padding-bottom:20px
}
.search {
    width:345px;

}
.header_search_button{
    float: right;
    height: 28px;
    line-height: 28px;
    border: none;
    border-radius: 5px;
    background-color: #eee;
}
.header_search_button:hover{ background-color: #fff;}
/*文章列表*/
#copost_container { margin-left: -16px; position:relative; }
#copost_container li { margin-top:2px; width: 280px; margin-left: 18.5px; -webkit-transition: all .7s ease-out .1s; -moz-transition: all .7s ease-out; -o-transition: all .7s ease-out .1s; transition: all .7s ease-out .1s; float: left; }
.copost_hover { padding:5px;   }
.copost_hover:hover { /*border-bottom: #b8c4d1 solid 1px; box-shadow: #fff 0px 0px 5px;*/}/*文章列表下划线*/
.cothumbnail { max-height: 500px; overflow: hidden; height:100px; }
.cothumbnail a { display: block; /*padding: 10px 10px 0 10px;*/ }
.cothumbnail img {min-width: 270px;  min-height:100px;height: auto; }
.coarticle { position:relative;  }/*高度*/
.coarticle h2{  line-height:3em; font-size:16px; font-weight:600;  }
.coarticle h2 a{ color:#444444; }
.coarticle h2 a:hover{ color:#fd6ca3;}
.coinfo {color: #444;  white-space: nowrap;text-overflow: ellipsis; position: relative; padding: 10px 0px; margin-top:-20px; font-size:12px;}
.coinfo span{font-weight:bold; line-height:1.8em}
.coentry_post { line-height: 22px; color: #666; margin-bottom: 5px; word-break: break-all; }
.sticky { background: #fd6ca3; height: 25px; width: 45px; position: absolute; z-index: 20; top: -1px; right: -1px; color: #fff; font-weight: bold; text-align: center; line-height: 25px; }
.ssticky { font-size:14px;color:#FFF;padding-left:8px;height: 70px;width: 72px; line-height:2.8em;display: block;overflow: hidden;background-position: -314px 0;position: absolute;left:0;top:0;z-index: 10;}
.icons,.flex-direction-nav li a{background: url("./images/icons.png") no-repeat;}
.arrow-catpanel-top { position: absolute; /*background: url(images/arrow-catpanel-top.png) no-repeat 0px 0px;*/ width: 52px; height: 14px; bottom:-1px; left: 130px; z-index: 10; }
.zoom { width: auto; height: auto; display: block; position: relative; overflow: hidden; background: none; }
/*

.zoomOverlay { position: absolute; top: 0; left: 0; bottom: 0; right: 0; display: none; !*margin: 10px 10px 0 10px;对应图像尺寸*! background-image: url(images/zoom.png); background-repeat: no-repeat; background-position: center; background-color:rgba(247, 164, 164, 0.97) !important}
*/

#copost_container .fixed-hight h2 a{ display:block;white-space: nowrap;text-overflow:ellipsis; overflow:hidden;}
#copost_container .fixed-hight .coentry_post{overflow: hidden;height: 42px;}
#copost_container .fixed-hight .coinfo{ overflow:hidden; height:140px; width:270px;}
#copost_container .fixed-hight .cothumbnail{height:110px;; overflow: hidden;}
.cobox { background: #fff; /*border: solid 1px #d9dbdd; border-bottom-color:#dcdee0;*/}
.coboxx{}

/*全屏幻灯代码*/
#sliderbox {
    position:relative;
    clear:both;
    overflow:hidden
}
#slidebanner {
    width:1900px;
    height:500px;
    margin-left:-950px;
    text-align:center;
    _text-align:left;
    overflow:hidden;
    position:relative;
    left:50%;
    z-index:90;
    clear:both
}
#slideshow li {
    width:1900px;
    height:500px;
    position:absolute;
    left:0;
    top:0
}
#slideshow li img {
    width:1900px;
    height:500px;
    display:block
}
#slidebanner .bx-wrapper {
    height:auto
}
#slidebanner .bx-wrapper .bx-pager {
    width:100%;
    text-align:center;
    position:absolute;
    left:0;
    bottom:10px;
    z-index:90
}
#slidebanner .bx-wrapper .bx-pager .bx-pager-item, #slidebanner .bx-wrapper .bx-controls-auto .bx-controls-auto-item {
    display:inline
}
#slidebanner .bx-wrapper .bx-pager a {
    margin-left:10px;
    width:48px;
    height:4px;
    font-size:0;
    background:#fff;
    overflow:hidden;
    display:inline-block;
    text-decoration:none;
    moz-border-radius:50px;
    -webkit-border-radius:50px;
    border-radius:50px
}
#slidebanner .bx-wrapper .bx-pager a.active {
    background:#2c4476
}
#sliderbox .bx-prev, #sliderbox .bx-next {
    width:60px;
    height:100%;
    _height:400px;
    text-indent:-9999px;
    background:url(images/arrow-slider.png) no-repeat -50px 48%;
    overflow:hidden;
    display:none;
    position:absolute;
    top:0;
    z-index:100;
    filter:alpha(opacity=60);
    -moz-opacity:.6;
    opacity:.6
}
#sliderbox .bx-prev {
    left:3%;
    _left:69%
}
#sliderbox .bx-next {
    right:3%;
    background-position:10px 48%
}
#sliderbox .bx-prev:hover, #sliderbox .bx-next:hover {
    filter:alpha(opacity=100);
    -moz-opacity:1;
    opacity:1
}
.bx-controls-auto {
    display:none
}
.banner-shadow {
    width:100%;
    height:25px;
    background:url(images/shadow.png) repeat;
    overflow:hidden
}
.banner {
    text-align:center;
    background:#eee;
    overflow:hidden;
    position:relative
}
.banner img {
    width:100%;
    display:block
}

/*mycss*/
#center_span{width: 450px;
    height: 60px;
    line-height: 60px;
    text-align: center;
    background: #fee9ea url(images/warning.png) no-repeat 5px center;
    border: 1px solid #de888a;
    -moz-border-radius: 5px;
    -webkit-border-radius: 5px;
    border-radius: 5px;
    font-size: 20px;
    margin: 0 auto;
    margin-bottom: 20px;


}
#center_title{color: red;}
#center_title:hover{color: deeppink}
#shenming{
    font-size: 15px;
    margin: 30px auto;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #f6ceba;
    color:#ff4500

}

#shenming p{
    padding: 0px;
    margin: 0;
    

}
#shenming p a{
color: blue;

}

#shenming .shenming_link a{
color: #ff4500

}


#download{
    margin: 1px auto;width: 100%;height: 100%;text-align: center;
}
#download a{display: inline-block;width: 300px;}
#download img:hover{
    opacity: 0.8;
}
.padd{display: none}
/*about*/
.about{width: 90%;padding: 15px;margin: 0 auto;text-align: center;background-color: white;transition: all 0.3s}
.about .about_tab{margin: 0 auto;height: auto;text-align: center;width: 350px;margin-bottom: 20px;}
.about .about_tab a{text-align: center;width: 150px;color: #666;height:40px;line-height: 40px;display:inline-block;margin: 0 1px;font-size: 18px;border:1px solid orangered;color: black;}
.about .about_tab .about_tab_one{background-color: orangered;color: white}
.about .about_tab a:hover{background-color: #fe652c;color: white}
.about .about_tab .about_tabl{border-radius: 20px 0px 0px 20px;}
.about .about_tab .about_tabr{border-radius: 0px 20px 20px 0px;}
.about .about_content{height: auto;margin-bottom: 200px;}
.about .about_content p{width: 80%;margin: 0 auto;font-size: 17px;line-height: 34px;color: #666}
.about .about_right{display: none}
.about .about_content h4{font-size: 25px;width:100%;text-align: center;margin-top: 40px;}
.about .about_content .about_mgs{width: 550px;height: 150px;margin:0 auto;background-image: linear-gradient(120deg, #f093fb 0%, #f5576c 100%);padding: 0 30px;margin: 20px auto;border-radius: 3px;transition: all 0.2s}
.about .about_content .about_mgs .about_mgsl{height: 100%;width:170px;;display: inline-block}
.about .about_content .about_mgs .about_mgsl img{width: 172px;height: 45px;position:relative;top: 50%;margin-top: -22px;}
.about .about_content .about_mgs .about_mgsr{width: 300px;height: 100%; ;float: right;padding:0;}
.about .about_content .about_mgs .about_mgsr p {font-size: 15px;line-height: 25px;color: #eee;margin: 0;width: 100%;margin-top: 10px;}
.about .about_content .about_mgs .about_mgsr .about_mgsr_title {color: white;font-size: 20px;font-family:verdana}

.about .about_content .about_dmm{background-image: linear-gradient(120deg, #84fab0 0%, #1fb835 100%);}
.about .about_content .about_dmm .about_mgsl  img{height: 75px;position:relative;top: 50%;margin-top: -37px;}
.about .about_content .about_r18{background-image: radial-gradient(circle 248px at center, #16d9e3 0%, #30c7ec 47%, #46aef7 100%);}
.about .about_content .about_r18 .about_mgsl img{height: 60px;position:relative;top: 50%;margin-top: -30px;}
.about .about_content .about_mgs:hover{-moz-box-shadow:0px 0px 20px #8C8C8C; -webkit-box-shadow:0px 0px 20px #8C8C8C; box-shadow:0px 0px 20px #8C8C8C;}
.about .about_content .about_if{width: 100%;text-align: center;font-size: 20px;color: black;margin: 40px 0;color: #666}

.about .about_content .about_contact{width: 100%;text-align: center;font-size: 20px;margin-top: 40px;}
.about .about_content .about_contact a{border: 1px solid #3498DB;padding: 10px 100px;transition: all 0.3s;border-radius: 20px;color: black;font-weight: 500;}
.about .about_content .about_contact a:hover{background-color: #3498DB;color: white;-moz-box-shadow:0px 0px 10px #8C8C8C; -webkit-box-shadow:0px 0px 10px #8C8C8C; box-shadow:0px 0px 10px #8C8C8C;}
.about .about_content .about_pc_qq{display: none;background-color: #f2dede;color: #b94a48;width: 286px;font-size: 14px;text-align: center;;height: auto;margin-top: 15px;border: 1px solid #eed3d7;border-radius: 5px;}
.about .about_content .about_mobile_qq{display: none;color: black;width: 100%;text-align: center}
.about .about_content .about_mobile_qq a{display: inline-block}

/*正在跳转付款页面*/
#open_js{position: absolute;top:180px;width: 200px;height:80px;text-align: center;left: 50%;margin-left: -100px;font-size: 14px;line-height: 20px;}
#open_js img{;display:block;margin:0 auto;width: 50px;margin-bottom: 15px}
#space{width: 35px;display: inline-block}

/*排序*/
.container .sort{width: 99%;height: 30px;;padding: 5px 2px;margin: 0 auto;background-color: #fff;margin-bottom:10px}
.container .sort .sort_left{height: 30px;line-height:30px;float: left;font-size: 16px;}
.container .sort .sort_right{height: 30px;line-height:30px;float: right;font-size: 16px;}


/*losePASS*/
.resetpass{background-color: #fff;text-align: center;padding: 20px;}
.page .content.resetpass{padding:20px;text-align:center;margin-right:0}
.resetpass form{width:300px;margin:0 auto;text-align:left}
.resetpass form p{margin-bottom:20px}
.resetpass form p .form-control{width: 200px;height: 30px;line-height: 30px;}
.resetpass form p .getstart{border: 1px solid #ff5f33;background-color: #ff5f33;text-align: center;font-size: 20px;color: #fff;padding: 10px 20px;width: 200px;}
.resetpass form p .getstart:hover{background-color:#f97652 }
.resetpass h1{font-size:24px;font-weight:normal;margin-bottom: 20px;}
.resetpass h3{color:#777;font-size: 24px;}
.resetpass h3 .glyphicon{top:4px}
.resetpasssteps{margin-bottom:50px;overflow:hidden}
.resetpasssteps li{width:33.33333%;text-align:center;float:left;background-color:#eee;color:#666;line-height:33px;position:relative;padding-left:15px;box-sizing: border-box;}
.resetpasssteps li.active{background-color:#E74C3C;color:#fff;text-align: center;}
.resetpasssteps li .glyphicon{position:absolute;right:-17px;top:-3px;font-size:36px;color:#fff;z-index:2}
.errtip{background-color:#FCEAEA;color:#DB5353;padding:8px 15px;font-size:14px;border:1px solid #FC9797;}

.tips_info{
    text-align: center;
    font-size: 15px;
    margin: 5px auto;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #54aaff;
    color:#1e88e5}
.tips_info a{color: deeppink}
.last_page{display: none}
.last_page a{font-size: 16px;padding: 10px 15px;background-color: #1e88e5;color: #fff;display: block;width: 110px;margin: 0 auto;margin-top: 20px;text-align: center}
.last_page a:hover{opacity: 0.8}

@media only screen and (min-width:1330px) {
    .container { max-width: 1180px; !important; }
    /*.slider { width: 1306px !important; }幻粉*/
    #focus ul li { width: 975px; }
    #focus ul li img { width: 666px; }
    #focus ul li a { float: none; }
    #focus .button { width: 975px; }
    .slides_entry { display: block !important; margin-top: 10px; font-size: 14.7px; line-height: 1.5em; }
    .flex-caption { left: 650px !important; width: 292px; bottom: 0 !important; height: 370px; /*border-bottom: 1px #999 dashed*/}/*左边高度*.1 */
    .flex-caption h2 { /*line-height: 1.5em; margin-bottom: 20px; padding: 10px 0 20px 0; */font-size: 14px;/* font-weight: bold;*/  }
    .flex-caption a:hover { color: #fd6ca3; }
    .flex-caption .btn { display: block !important; margin-top: 30px; width: 55px; }
    .flex-caption .btn a { color: #fd6ca3; }
    #focus ul li a img { width: 975px !important; }/*幻灯全屏*/
    .related_box{ width:158px !important}
}
@media (max-width: 1220px) {
    #center_title {
        font-size: 16px;
        font-weight: normal
    }
    #center_span {
        width: 300px;
        height: 35px;
        line-height: 35px;
        background: #fee9ea url() no-repeat 0px center
    }
  #post_content img{height: auto}
}
@media (max-width: 1201px) {
    .topnav ul li a:link {}
    .topnav{margin: 0 auto;padding: 0 10px;}
    .search-button-top button{margin-right: 50px;}
    .mainleft{text-align: center;}
    #post_container{text-align: center;width:100%;margin: 0 auto;}
    .thumbnail img{min-width: 220px;}
    #post_container li{width: 220px;float:none;display: inline-block}
    #post_container .fixed-hight .thumbnail{height: 125px;}
    .article{padding: 5px 2px 0px 2px}
    .article h2{font-size: 10px;font-weight: 400}
    .pagination{text-align: center}
}

@media only screen and (min-width:1024px)and (max-width:1200px) {
    .related { width: 100% }
    .related ul { width: 600px;  }
    .related ul li{ width:250px; height:180px;}
    .related_box { float: left; width: 280px; height: 285px;}
    .related_box:hover { background-color:#f0f2f7;  }/*颜色*/
    .related_box a:hover {color:#779ed4 }
    .related_box .r_title { padding: 0 8px; text-align: center; }
    .related_box .r_pic { margin: 8px auto; width: 140px; height: 94px;}
    .related_box .r_pic img { width: 140px; height: 94px; }
    #blognamess{ display: none  }
    .subsidiary,.archive-header-ad{ display: none !important; }
    .adphone{display:none;}
    .left {  float:left }
    .indexPart2Right ul li{ list-style-type: decimal; }
    .indexPart2Right {
        border-radius:5px;
        /*background-color:#FFF;*/
        width:200px;
        height:auto;
        padding:20px 10px 20px 10px;
        margin-left:20px;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }
    .indexPart2Right:hover { /*border-bottom: #b8c4d1 solid 1px; box-shadow: #b8c4d1 0px 0px 5px;*/}/*文章列表下划线*/
    .indexPart2Right li {
        width:260px;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        margin-top:5px;
        _margin-top:14px;
    }
    .indexPart2Right li a {
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        width:260px;
        color:#666;
        font-size:12px;
    }
    .indexPart2Right li a:hover {
        color:#fd6ca3;
        /*text-decoration:underline;*/
    }
    .indexPart2Right li span {
        display:inline-block;
        margin-right:8px;
        background:#ff6100;
        width:22px;
        text-align:center;
        color:#fff;
        transition:all .5s ease-out;
        -webkit-transition:all .5s ease-out;
        -moz-transition:all .5s ease-out;
        -o-transition:all .5s ease-out;
        -ms-transition:all .5s ease-out
    }
    .indexPart2Right li:hover span {
        transform:rotate(360deg);
        -webkit-transform:rotate(360deg);
        -ms-transform:rotate(360deg);
        -moz-transform:rotate(360deg)
    }
    .indexPart2Right h3 {
        font:bold 14px/normal 'MicroSoft Yahei';
        color:#ddd;
        /*border-bottom:3px solid #eff2f5;*/
        width:260px;
    }
    .indexPart2Right h3 span a {
        float:right;
        font-size:12px;
        color:#666;
        background-color:#222222;
        padding:0 5px;
        border-radius:3px;
    }
    .indexPart2Right h3 span a:hover {
        float:right;
        font-size:12px;
        color:#fff;
        background-color:#fd6ca3;
        padding:0 5px;
        border-radius:3px;
    }
    .fens{
        background-color:#141414;

        padding-top:20px;
        padding-bottom:20px;
    }
}

@media(max-width:980px) {
    .adphone,.related{display:block;}
    #blognamess{display: none}
    #shenming .shenming_link{display: none}
}

@media only screen and (max-width:900px){
    #post_container li:hover{top:0px}
    .topnav .menu-item-has-children .menu-children-ico{display: inline-block;}
    .topnav .menu-item-has-children:after{content: '';border: none;}
    .related { float:left }
    .related ul { width: 600px;  }
    .related ul li{ width:280px; height:180px;float:left; margin-right:20px;}
    .related_box { float: left; width: 280px; height: 285px;}
    .related_box:hover { background-color:#f0f2f7;  }/*颜色*/
    .related_box a:hover {color:#779ed4 }
    .related_box .r_title { padding: 0 8px; text-align: center; }
    .related_box .r_pic { margin: 8px auto; width: 140px; height: 94px;}
    .related_box .r_pic img { width: 140px; height: 94px; }
    /*菜单*/
    .search-button-top button{display: none}
    .topnav{height: 50px;}
    .topnav{overflow: visible;}
  .topnav ul ul{background-color: #222222}
    .topnav .menu-button{  display:block;  float: left;  top:8px;  left: 10px;  width: 74px;}
    #header-bottom-right{width: 120px;top:8px;right: 0px;z-index: 9999 ;position: absolute;float: right;padding: 0;margin: 0;display: inline-block;}
    #header-bottom-right .search{  width:94%;overflow:hidden;height: 30px;  line-height: 30px;  padding: 0px;  margin: 0px; border: none}
    #header-bottom-right .search-field-holder .sousuo{;padding:0;position: absolute;  background: url("images/search-bottom.png") center no-repeat;  background-size: 80%;  width: 40px;  height: 30px;
        border: none;
        right: 0;top: 0}
    #header-bottom-right .search-field-holder{display: inline-block;height: auto;vertical-align: top;position: relative}
    #header-bottom-right .search-field-holder .search-field{width: 120px;}
    .search-icon{display: none}
    #menus{ display:none;padding:30px 0px 15px 0px; }
    #menus.open{ display:block; -webkit-transition: all .5s ease-in-out; -moz-transition: all .5s ease-in-out; -ms-transition: all .5s ease-in-out; transition: all .5s ease-in-out;}
    .container{padding: 10px}
    #menus li{ height:40px;width:100%;margin-left: 5px;margin-bottom:3px;}
    #menus li a{width:100% !important;line-height:40px;height:40px;font-size: 14px;}
    #menus li a:hover{text-indent: 0px}
    #menus .menu-item-has-children{height: auto;position: relative}
    #menus .menu-item-has-children .chevron-down{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico:active{background-color: #ef5b9c}
    #menus .menu-item-has-children ul li a{}
    .topnav a{height: 40px;}
    .topnav li .sub-menu{ position:relative;width: 100%; top:0; left:0px;display: none;opacity: 1;overflow: auto;}
    .topnav ul ul li{color: #cecdcd}
    #menus .sub-menu li{width: auto;display: inline-block;}
    #menus .sub-menu li a{color: #cecdcd}
    .topnav li .sub-menu:before{ content: '';border: none;}
}

@media (max-width: 884px) {
    .search-button-top button{margin-right: 4px;}
    .topnav ul li a:link{padding: 3px 4px 0 4px}
    .topnav{height:60px;}
    .topnav li{height: 60px;}
    .topnav a{line-height: 50px;}
    .topnav ul li a:link{font-size: 10px;}
    .article_container h1{font-size: 1.0em}
}
@media (max-width: 750px) {
    #post_container li{width: 40%}
    #post_container .fixed-hight .thumbnail{height: auto}
    .thumbnail img{width: 100%}
    #post_container li{padding: 0}
    #post_container .fixed-hight h2 a{font-weight: 400}

}
@media  (max-width: 725px){
    .thumbnail img{min-width: 260px;}
    #post_container li{min-width: 260px}
  #mgssd_tips{display: none}
}

@media (max-width: 650px){
    /* #download{display: block}*/
    .topnav .menu-button{left: 0px;}
  .topnav ul ul{background-color: #31302E}

    .padd{display: block;height: 10px;}
    #header-bottom-right{width: 90px;}
    #header-bottom-right .search-field-holder .search-field{width: 75px;}
    .article h2{font-size:12px;font-weight: 600}
    .search-button-top button{display: none}
    .topnav{height: 50px;}
    .article_container{padding: 5px;}
    .pagination{font-size: 12px;}
    .mainmenus { margin-bottom: 1.5em; background-color: #edf1f7;box-shadow: none;}
    .mainmenus .container {background-color: #313030 }
    #sidebar,.subsidiary, .slider, #rss, .banner,.extend, .article_related,#head,.slider,.fens,.subsidiarys,.sthumbnail,.sinfo,.menu-right,#authorarea ,#blogname,#container,.related,.tximgcc{ display: none !important; }
    .mainleft { margin: 0 auto; overflow:visible}

    #comment-author-info { height: auto; }
    #comment-author-info input { width: 60.5%; margin-bottom: 5px; }
    .search_phone { display: block }
    #post_container{ margin-left:0}
    /*#post_container li{ width:100%; margin-left:0; max-width:100%}*/
    #post_container li{min-width:auto;width: 48%;margin-left: 1px;}
    #post_container li .thumbnail a{ text-align:center}
    #post_container li .arrow-catpanel-top{ display:none}
    #post_container li .zoomOverlay{ display:none !important}
    #copost_container{ margin-left:0}
    #copost_container li{ width:100%; margin-left:0; max-width:100%}
    #copost_container li .cothumbnail a{ text-align:center}
    #post_container li .thumbnail a img{min-width: auto;width: 100%}
    #copost_container li .arrow-catpanel-top{ display:none}
    #copost_container li .zoomOverlay{ display:none !important}
    #post_container .fixed-hight .thumbnail{height: auto;}
    #tbox{ right:0;}
    .topnav ul ul li a:link, .topnav ul ul li a:visited{}

    #header-bottom-right .search-field-holder .sousuo{width: 30px;}
  .resetpasssteps li{display: block;width: 100%}
/*	.topnav{overflow: visible;}
    .topnav .menu-button{  display:block;  float: left;  top:8px;  left: 10px;  width: 74px;}
    #menus{ display:none;padding:30px 0px 15px 0px; background-color: #313030}
    #menus.open{ display:block; -webkit-transition: all .5s ease-in-out; -moz-transition: all .5s ease-in-out; -ms-transition: all .5s ease-in-out; transition: all .5s ease-in-out;}
    .container{padding: 10px}
    #menus li{ height:40px;width:100%;margin-left: 10px;margin-bottom:5px;border-bottom: 1px solid #1c1c1c;}
    #menus li a{width:90% !important;line-height:40px;height:40px;font-size: 14px;}
    #menus li a:hover{text-indent: 0px}
    #menus .menu-item-has-children{height: auto;position: relative}
    #menus .menu-item-has-children .chevron-down{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico{position: absolute;padding: 12px;right: 0;top:0;}
    #menus .menu-children-ico:active{background-color: #ef5b9c}
    #menus .menu-item-has-children ul li a{background-color: #313030}
    .topnav a{height: 40px;}
    .topnav li .sub-menu{ position:relative; top:0; left:0px;display: none;opacity: 1}
    .topnav ul ul li{color: #cecdcd}
    #menus .sub-menu li{width: auto;}
    #menus .sub-menu li a{color: #cecdcd}
    .topnav li .sub-menu:before{ content: '';border: none;}*/
    #post_content h3 strong{font-size: 13px}
    #home,#pinglun{display: none}
    .navigation{width: 100%}
    .pagination a, .pagination span{width: 40px;height: 25px;line-height: 25px;}
    .pagination .current { height: 25px; width:40px;color: #fd6ca3; border-style:solid; border-width:1px; border-color:#fd6ca3; margin: 10px 5px;}
    .page_previous, .pagination .prev{width: 50px;height: 25px;}
    .pagination .page_next, .pagination .next, .pagination .page_next:hover, .pagination .next:hover { width: 50px;height: 25px; text-align: center; }
    .pagination .prev:hover{;width:50px;height: 25px;;line-height: 25px;}
    .pagination a:hover{width: 40px;height: 25px;line-height: 25px;}
    .article_container h1{font-size: 0.8em}
    #download a{width: 160px;}
    #about_container{min-width: 95% !important;}
    #about_mainleft{width: 100%}
    .about .about_content p{width: 95%}
    .about .about_content .about_mgs{height: 215px;width:80%;}
    .about .about_content .about_mgs .about_mgsl{display: block;width:100%;height: auto;text-align: center}
    .about .about_content .about_mgs .about_mgsr{display: block;width: 100%;height: 100px;text-align: center}
    .about .about_content .about_mgs .about_mgsl img{top:0;margin-top: 15px;}
    .about .about_content .about_mobile_qq{display: block;}
    .about .about_content .about_contact{display: none}
}
@media  (max-width: 395px){
    .about{min-width: 300px;}

    .about .about_tab{width: 100%;}
    .about .about_tab a{width: 40%;}
    .about .about_hide{display: none}
    .about .about_content p{line-height: 28px;width: 100%}
    .about .about_content .about_mgstage{height:230px;}
    .about .about_content .about_contact a{padding: 10px 70px;}
}
.after_qq:after{content: "QQ1405617552"}
.after_emil:after{content: ""}
.footer_warning{font-size: 12px;color: orangered }
.footer_warning:after{content: "提示："}
