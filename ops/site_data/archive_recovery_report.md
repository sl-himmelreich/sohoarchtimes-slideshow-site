# Archive image recovery report

Generated: 2026-05-16 10:09:41 UTC

## Summary

- Telegram-preview posts targeted: 82
- Cache entries: 82
- Fully recovered (exactly 5 source_image_urls): 82
- Partial: 0
- Failed: 0
- Cache file: `/home/user/workspace/sohoarchtimes_site_data/recovered_source_images_cache.json`
- Recovery script: `/home/user/workspace/recover_archive_source_images.py`

## Method

- ArchDaily: extract `images.adsttc.com/media/images/...` gallery URLs from DOM and embedded page data; normalize `thumb_jpg`, `medium_jpg`, and `newsletter` variants to `large_jpg`; deduplicate by media id; keep the first 5 gallery images.
- Parametric Architecture: resolve stale slugs through WordPress REST search, parse article image tags and srcsets, prefer high-resolution/scaled uploads, filter logos/avatars/sidebar thumbnails, deduplicate WordPress attachment variants, keep the first 5 quality images.
- Other domains: generic image extraction from main HTML, OpenGraph, and srcsets with the same garbage-image filters; used only as a fallback.
- Build integration: `build_sohoarchtimes_catalog.py` loads the build-compatible `recovered_source_payloads.json` generated from the recovery cache and uses recovered images when local payload images are missing.

## Domain coverage

- www.archdaily.com: 60
- parametric-architecture.com: 17
- www.unstudio.com: 3
- jmayerh.de: 1
- www.toyo-ito.co.jp: 1

## Recovered posts

| message_id | title | status | candidates | resolved_source_url | first image |
|---:|---|---|---:|---|---|
| 23 | Beyond the Geometry Plastic 3D Printed Pavilion | recovered | 27 | https://www.archdaily.com/960939/beyond-the-geometry-the-worlds-largest-modified-plastic-3d-printing-architecture-archi-union-architects | https://images.adsttc.com/media/images/608b/c012/f91c/81e5/a900/001b/large_jpg/22.jpg?1619771357 |
| 40 | Crosslight Wedding Chapel | recovered | 14 | https://parametric-architecture.com/crosslight-wedding-chapel/ | https://parametric-architecture.com/wp-content/uploads/2025/07/crosslight-wedding-chapel-ideorealm-design-yiwen-xu-02.webp |
| 45 | Studio Ardete Headquarters | recovered | 24 | https://parametric-architecture.com/studio-ardetes-headquarters-facade/ | https://parametric-architecture.com/wp-content/uploads/2025/02/Shaping-a-Living-Facade-at-Studio-Ardetes-Headquarters-in-Mohali-7-scaled.webp |
| 51 | Beeah Headquarters | recovered | 24 | https://parametric-architecture.com/beeah-headquarters-sharjah-case-study/ | https://parametric-architecture.com/wp-content/uploads/2025/03/ZHA-Beeah-Headquarters-HuftonCrow-01.webp |
| 56 | Ascentage Pharmaceutical Headquarters | recovered | 11 | https://parametric-architecture.com/ascentage-pharmaceutical-headquarters-oli-architecture/ | https://parametric-architecture.com/wp-content/uploads/2024/01/Ascentage-Pharmaceutical-Headquarters-17.jpg |
| 66 | Al Bahar Towers Responsive Facade | recovered | 5 | https://www.archdaily.com/270592/al-bahar-towers-responsive-facade-aedas | https://images.adsttc.com/media/images/5d53/11e8/284d/d173/7600/009a/large_jpg/CST4r0EWwAA8l5b.jpg?1565725154 |
| 71 | Generative Design Pavilion | recovered | 20 | https://www.archdaily.com/804456/autodesks-generative-design-pavilion-plays-with-properties-and-fabrication-processes-in-stone-and-fabric | https://images.adsttc.com/media/images/5890/e603/e58e/ceb7/6c00/0028/large_jpg/AU_Generative_Design_Pavilion_(9_of_31).jpg?1485891056 |
| 76 | ICD/ITKE Research Pavilion 2014-15 | recovered | 30 | https://www.archdaily.com/770516/icd-itke-research-pavilion-2014-15-icd-itke-university-of-stuttgart | https://images.adsttc.com/media/images/55ac/ee20/e58e/ce12/db00/023f/large_jpg/ICD-ITKE_RP13-14_Image01.jpg?1437396506 |
| 81 | Mushroom Pavilion at Casa Wabi | recovered | 22 | https://parametric-architecture.com/oma-mushroom-pavilion-at-casa-wabi/ | https://parametric-architecture.com/wp-content/uploads/2026/03/Mushroom-Pavilion-05.webp |
| 86 | L’île Folie Pavilion | recovered | 26 | https://parametric-architecture.com/lile-folie-pavilion-theverymany/ | https://parametric-architecture.com/wp-content/uploads/2026/03/Lile-Folie-Pavilion-Marc-Fornes-THEVERYMANY-Kroo-Photography-01.webp |
| 91 | Kulhad Pavilion for Serendipity Arts Festival 2025 | recovered | 23 | https://parametric-architecture.com/wallmakers-kulhad-pavilion/ | https://parametric-architecture.com/wp-content/uploads/2026/02/Kulhad-Pavilion-Wallmakers-Studio-IKSHA-06-1.webp |
| 96 | Cappella del Suono | recovered | 16 | https://parametric-architecture.com/cappella-del-suono-pavilion-italy/ | https://parametric-architecture.com/wp-content/uploads/2026/01/Capella-Del-Suono-01.webp |
| 131 | PILOTI Pavilion | recovered | 20 | https://parametric-architecture.com/piloti-pavilion-by-marc-fornes/ | https://parametric-architecture.com/wp-content/uploads/2025/09/PILOTI-Pavilion-cover.webp |
| 136 | Pier 865 | recovered | 23 | https://parametric-architecture.com/pier-865-by-marc-fornes-theverymany/ | https://parametric-architecture.com/wp-content/uploads/2025/12/Pier-865-by-Marc-Fornes-THEVERYMANY-Steve-Kroodsma-09-scaled.webp |
| 156 | Хейдар Алиев Центр | recovered | 15 | https://parametric-architecture.com/heydar-aliyev-cultural-center-study/ | https://parametric-architecture.com/wp-content/uploads/2025/02/Heydar_Aliyev_Center_ZHA_03-scaled.webp |
| 166 | SOFTSTONE Office Building | recovered | 14 | https://parametric-architecture.com/softstone-office-building-by-setuparchitecture/ | https://parametric-architecture.com/wp-content/uploads/2020/03/17_SOFTSTONE-_-SETUParchitecture-Sina-Mostafavi-scaled.jpg |
| 171 | Bund Finance Centre | recovered | 28 | https://parametric-architecture.com/bund-finance-centre-by-foster-partners-and-heatherwick-studio/ | https://parametric-architecture.com/wp-content/uploads/2018/10/PA_Bund_Finance_Centre_1.jpg |
| 176 | Communique Headquarters | recovered | 18 | https://www.archdaily.com/780596/communique-headquarters-daewha-kang-design | https://images.adsttc.com/media/images/569e/1b06/e58e/cef0/8400/00d4/large_jpg/02_DKD_Communique_Silver_Tree.jpg?1453202171 |
| 201 | Loop of Wisdom Museum & Reception Center | recovered | 33 | https://www.archdaily.com/949622/loop-of-wisdom-museum-powerhouse-company | https://images.adsttc.com/media/images/5f88/536e/63c0/17d6/a100/007d/large_jpg/Powerhouse_Company_-_Loop_of_Wisdom_-_photo_by_Jonathan_Leijonhufvud_25.jpg?1602769766 |
| 221 | New Science and Technology Museum of Henan Province | recovered | 48 | https://www.archdaily.com/1034203/new-science-and-technology-museum-of-henan-province-tjad-atelier-l-plus | https://images.adsttc.com/media/images/68c9/d839/8791/b754/e13d/02eb/large_jpg/new-science-and-technology-museum-of-henan-province-tjad-atelier-l-plus_15.jpg?1758058563 |
| 231 | Maslak No.1 Office Tower | recovered | 36 | https://www.archdaily.com/800160/maslak-n-office-tower-emre-arolat-architects | https://images.adsttc.com/media/images/5837/9fab/e58e/ce93/1c00/0043/large_jpg/161005D0018.jpg?1480040358 |
| 246 | Da Nang Hi-Tech Park Headquarters Building | recovered | 18 | https://www.archdaily.com/1027308/da-nang-hi-tech-park-headquarters-building-huni-architectes | https://images.adsttc.com/media/images/67bc/96e6/fc55/de00/0148/2314/large_jpg/HTP01.jpg?1740412659 |
| 251 | Morpheus Hotel | recovered | 57 | https://www.archdaily.com/896433/morpheus-hotel-zaha-hadid-architects | https://images.adsttc.com/media/images/5b22/972a/f197/cc06/de00/0020/large_jpg/15_ZHA_Morpheus_photo_Virgile_Simon_Bertrand.jpg?1528993439 |
| 256 | Lumina Shanghai | recovered | 29 | https://www.archdaily.com/989776/lumina-shanghai-gensler | https://images.adsttc.com/media/images/6335/74b3/4dba/6e44/26c9/512b/large_jpg/not-ready-lumina-shanghai-gensler_2.jpg?1664447694 |
| 276 | One Thousand Museum Residential Tower | recovered | 26 | https://parametric-architecture.com/one-thousand-museum-residential-tower-erected-by-zaha-hadid-architects/ | https://parametric-architecture.com/wp-content/uploads/2021/08/PA_1000MUSEUM-9.jpg |
| 301 | Metropolitan Railway Station | recovered | 13 | https://parametric-architecture.com/metropolitan-railway-station-features-mushroom-pillars-made-of-latticed-steel/ | https://parametric-architecture.com/wp-content/uploads/2024/05/Metropolitan-Railway-Station-14.jpg |
| 311 | Port House | recovered | 23 | https://parametric-architecture.com/zaha-hadid-port-house-floating-crystal/ | https://parametric-architecture.com/wp-content/uploads/2025/07/ZHA-Port-House-01.webp |
| 321 | CMA CGM Headquarters | recovered | 19 | https://www.archdaily.com/351657/zaha-hadid-architects-first-built-tower-cma-cgm-headquarters | https://images.adsttc.com/media/images/5154/3957/b3fc/4b41/6b00/007d/large_jpg/ZH_CMA-CGM_Marseille_%C2%A9Hufton_Crow_035.jpg?1364474170 |
| 341 | King Abdullah Financial District Metro Station | recovered | 20 | https://www.archdaily.com/1024201/king-abdullah-financial-district-metro-station-zaha-hadid-architects | https://images.adsttc.com/media/images/6749/cb6c/a36f/6233/c0a6/e9c9/large_jpg/king-abdullah-financial-district-metro-station-zaha-hadid-architects_2.jpg?1732889496 |
| 346 | Shanghai Tower | recovered | 40 | https://www.archdaily.com/783216/shanghai-tower-gensler | https://images.adsttc.com/media/images/56da/0955/e58e/ce77/ee00/0006/large_jpg/HIPWF_ShanghaiTower_ZhonghaiShen_141201_038.jpg?1457129803 |
| 361 | Harbin Opera House | recovered | 34 | https://www.archdaily.com/778933/harbin-opera-house-mad-architects | https://images.adsttc.com/media/images/5671/7b18/e58e/cec5/7900/0005/large_jpg/MAD_Harbin_Opera_House_001_©Hufton_Crow.jpg?1450277641 |
| 366 | World Trade Center Transportation Hub | recovered | 58 | https://www.archdaily.com/783965/world-trade-center-transportation-hub-santiago-calatrava | https://images.adsttc.com/media/images/5850/5b9b/e58e/ce32/8a00/0004/large_jpg/SC_Oculus_019.jpg?1481661331 |
| 371 | Пример параметрической архитектуры задолго до того, как в Москве её окрестили «э | recovered | 16 | https://www.archdaily.com/422470/ad-classics-the-guggenheim-museum-bilbao-frank-gehry | https://images.adsttc.com/media/images/521f/a052/e8e4/4eb9/4a00/0034/large_jpg/Flickr_User_RonG8888.jpg?1377804365 |
| 396 | Пример параметрической архитектуры задолго до того, как в Москве её окрестили «э | recovered | 16 | https://www.archdaily.com/248138/new-milan-trade-fair-studio-fuksas | https://images.adsttc.com/media/images/5018/9edc/28ba/0d5d/5d00/00b5/large_jpg/stringio.jpg?1414296326 |
| 406 | Пример параметрической архитектуры задолго до того, как в Москве её окрестили «э | recovered | 20 | https://jmayerh.de/metropol-parasol/ | https://jmayerh.de/files/2020/05/01-shop-harpersbazaar-com-feb-2019-walking-on-sunshine-sev-beige006.jpg |
| 411 | Пример параметрической архитектуры задолго до того, как в Москве её окрестили «э | recovered | 52 | https://www.archdaily.com/448774/heydar-aliyev-center-zaha-hadid-architects | https://images.adsttc.com/media/images/5285/1f2b/e8e4/4e52/4b00/01ab/large_jpg/HAC_photo_by_Iwan_Baan_(2).jpg?1384455904 |
| 416 | Национальный театр Тайчжуна | recovered | 5 | http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/2015-p_04_en.html | http://www.toyo-ito.co.jp/WWW/Project_Descript/2015-/2015-p_04/main photo.jpg |
| 421 | Absolute Towers | recovered | 10 | https://www.archdaily.com/306566/absolute-towers-mad-architects | https://images.adsttc.com/media/images/50c8/c96c/b3fc/4b70/6200/0008/large_jpg/Absolute_MAD_1020_by_iwan_baan.jpg?1413994233 |
| 431 | Museum of the Future | recovered | 12 | https://www.archdaily.com/983458/overcoming-design-challenges-with-technology-museum-of-the-future-in-dubai | https://images.adsttc.com/media/images/62b3/2622/2c50/db01/6721/f0d8/large_jpg/overcoming-design-challenges-with-technology-museum-of-the-future-in-dubai_2.jpg?1655907902 |
| 436 | National Museum of Qatar | recovered | 41 | https://parametric-architecture.com/national-museum-of-qatar-by-atelier-jean-novel/ | https://parametric-architecture.com/wp-content/uploads/2019/04/natianal-museum-jean-novel-pa-7.jpg |
| 441 | Leeza SOHO | recovered | 37 | https://www.archdaily.com/928726/leeza-soho-zaha-hadid-architects | https://images.adsttc.com/media/images/5dd4/02c4/3312/fda2/f100/009d/large_jpg/07_ZHA_Leeza_©Hufton_Crow.jpg?1574175416 |
| 446 | Dongdaemun Design Plaza | recovered | 39 | https://www.archdaily.com/489604/dongdaemun-design-plaza-zaha-hadid-architects | https://images.adsttc.com/media/images/5331/11d3/c07a/80d6/4200/007e/large_jpg/ZHA_DPPSeoul_VSB_01.jpg?1395724747 |
| 451 | The Yas Hotel | recovered | 18 | https://www.archdaily.com/43336/the-yas-hotel-asymptote | https://images.adsttc.com/media/images/5012/073c/28ba/0d55/8100/027f/large_jpg/stringio.jpg?1361409426 |
| 456 | Louvre Abu Dhabi | recovered | 93 | https://www.archdaily.com/883157/louvre-abu-dhabi-atelier-jean-nouvel | https://images.adsttc.com/media/images/5a01/bfaa/b22e/38b1/dc00/04e1/large_jpg/4._Louvre_Abu_Dhabi_-_Interior_view_1_©_Louvre_Abu_Dhabi_–_Photography_Roland_Halbe.jpg?1510064029 |
| 461 | Opus | recovered | 32 | https://www.archdaily.com/922310/opus-hotel-zaha-hadid-architects | https://images.adsttc.com/media/images/5d44/b144/284d/d1c3/7400/000c/large_jpg/07_ZHA_Opus_Dubai_photo_laurianghinitoiu.jpg?1564782879 |
| 471 | Guangzhou Opera House | recovered | 30 | https://www.archdaily.com/115949/guangzhou-opera-house-zaha-hadid-architects | https://images.adsttc.com/media/images/5013/88c6/28ba/0d15/0700/072b/large_jpg/stringio.jpg?1361420814 |
| 481 | Chaoyang Park Plaza | recovered | 30 | https://www.archdaily.com/884841/chaoyang-park-plaza-mad-architects | https://images.adsttc.com/media/images/5a25/b154/b22e/38dd/5d00/03db/large_jpg/MAD_Chaoyang_Park_Plaza_12_by_Hufton_Crow.jpg?1512419657 |
| 486 | Galaxy SOHO | recovered | 34 | https://www.archdaily.com/294549/galaxy-soho-zaha-hadid-architects-by-hufton-crow | https://images.adsttc.com/media/images/50a6/42f8/b3fc/4b46/eb00/0066/large_jpg/ZH_Galaxy_Soho_014.jpg?1375809655 |
| 491 | Beijing Daxing International Airport | recovered | 40 | https://www.archdaily.com/925536/beijing-daxing-international-airport-zaha-hadid-architects | https://images.adsttc.com/media/images/5d8c/b1e7/284d/d1d3/0f00/071d/large_jpg/09_ZHA_Beijing_Daxing_Int_Airport_®Hufton_Crow.jpg?1569501655 |
| 496 | Международный аэропорт Шэньчжэнь Баоань, Терминал 3 | recovered | 36 | https://www.archdaily.com/472197/shenzhen-bao-an-international-airport-studio-fuksas | https://images.adsttc.com/media/images/52e9/8df6/e8e4/4ea6/6300/00b7/large_jpg/©_Archivio_Fuksas_Untitled_Panorama2_2.jpg?1391037936 |
| 501 | Библиотека Биньхай в Тяньцзине | recovered | 24 | https://www.archdaily.com/882819/tianjin-binhai-library-mvrdv-plus-tianjin-urban-planning-and-design-institute | https://images.adsttc.com/media/images/59fb/061f/b22e/3822/4600/01c8/large_jpg/35b_Tianjin_Library_%C2%A9Ossip.jpg?1509623322 |
| 506 | Дом музыки в Будапеште | recovered | 17 | https://www.archdaily.com/1001574/house-of-music-budapest-sou-fujimoto-architects | https://images.adsttc.com/media/images/6470/937f/8e31/b832/174d/6c72/large_jpg/house-of-music-budapest-sou-fujimoto-architects_9.jpg?1685099460 |
| 516 | Башня MahaNakhon | recovered | 17 | https://www.archdaily.com/964053/mahanakhon-buro-ole-scheeren | https://images.adsttc.com/media/images/60d8/f591/f91c/81d2/c500/00a4/large_jpg/MahaNakhon_by_Buro_Ole_Scheeren_©_Buro-OS_13_Photo_by_Wison_Tungthunya.jpg?1624831333 |
| 526 | Aqua Tower | recovered | 12 | https://www.archdaily.com/42694/aqua-tower-studio-gang-architects | https://images.adsttc.com/media/images/5012/004e/28ba/0d55/8100/00e2/large_jpg/stringio.jpg?1361423963 |
| 531 | Capital Gate | recovered | 34 | https://www.archdaily.com/889854/capital-gate-rmjm | https://images.adsttc.com/media/images/5a96/5281/f197/ccd4/d000/00db/large_jpg/Capital_Gate_3.jpg?1519800951 |
| 536 | Shenzhen Energy Mansion | recovered | 25 | https://www.archdaily.com/899785/shenzhen-energy-mansion-big | https://images.adsttc.com/media/images/5b69/f0fc/f197/cc60/7f00/018f/large_jpg/copyright_laurianghinitoiu_big_shenzhen-9775_original.jpg?1533669572 |
| 541 | The Twist Museum | recovered | 24 | https://www.archdaily.com/925106/the-twist-museum-big | https://images.adsttc.com/media/images/5d82/2b66/284d/d153/e100/003f/large_jpg/02_BIG_KIS_The-Twist_Image-by-Laurian-Ghinitoiu.jpg?1568811835 |
| 566 | Centre Pompidou-Metz | recovered | 14 | https://www.archdaily.com/490141/centre-pompidou-metz-shigeru-ban-architects | https://images.adsttc.com/media/images/5332/4e7b/c07a/806c/3600/0084/large_jpg/POMPIDOU_METZ_321.jpg?1395805801 |
| 606 | Qatar National Convention Centre | recovered | 12 | https://www.archdaily.com/425521/qatar-national-convention-centre-arata-isozaki | https://images.adsttc.com/media/images/5229/0ef9/e8e4/4e5f/df00/00c6/large_jpg/ARATA_ISOZAKI_RHWL_QNCC_DOHA_QATAR_PAN_060313_0012.jpg?1378422514 |
| 616 | Rolex Learning Center | recovered | 12 | https://www.archdaily.com/53536/rolex-learning-center-sanaa-by-iwan-baan | https://images.adsttc.com/media/images/5008/acbc/28ba/0d50/da00/16d8/large_jpg/stringio.jpg?1361399480 |
| 621 | Shenzhen Science & Technology Museum | recovered | 32 | https://www.archdaily.com/1029762/shenzhen-science-and-technology-museum-zaha-hadid-architects | https://images.adsttc.com/media/images/6818/af5d/015c/4f01/7f12/2525/large_jpg/shenzhen-science-and-technology-museum-zaha-hadid-architects_2.jpg?1746448240 |
| 646 | Arnhem Central Transfer Terminal | recovered | 29 | https://www.archdaily.com/777495/arnhem-central-transfer-terminal-unstudio | http://s3.amazonaws.com/images.adsttc.com/media/images/564e/6751/e58e/ce4d/7300/0390/large_jpg/%C2%A9Ronald_Tilleman_20151108-0366-Pano.jpg?1447978804 |
| 651 | Mercedes-Benz Museum | recovered | 12 | https://www.unstudio.com/projects/mercedes-benz-museum | https://a.storyblok.com/f/324448/3000x2000/4c67c2457c/axo089_n132_wwwkits.jpg |
| 656 | Raffles City Hangzhou | recovered | 31 | https://www.archdaily.com/879869/raffles-city-hangzhou-unstudio | https://images.adsttc.com/media/images/59bf/d8bf/b22e/38c6/fe00/0120/large_jpg/cJin_Xing_LFS1.jpg?1505745078 |
| 661 | Galleria Centercity | recovered | 13 | https://www.archdaily.com/125125/galleria-centercity-unstudio | https://images.adsttc.com/media/images/55e8/9896/46fe/9f1d/fb00/0096/large_jpg/08_centercity_kim-yong-kwan_03.jpg?1441306749 |
| 686 | Wasl Tower | recovered | 12 | https://www.unstudio.com/projects/wasl-tower/ | https://a.storyblok.com/f/324448/8192x5456/37f7123832/wasl-tower-drone-270226-044.jpg |
| 691 | Doha Metro Network | recovered | 12 | https://www.unstudio.com/projects/doha-metro/ | https://a.storyblok.com/f/324448/7298x6776/3c20b34952/hero-alt.jpg |
| 711 | Huawei Flagship Store | recovered | 13 | https://www.archdaily.com/1012862/huawei-flagship-store-unstudio | https://images.adsttc.com/media/images/65bb/f1d4/87f3/9376/5913/1713/large_jpg/huawei-flagship-store-unstudio_1.jpg?1706816193 |
| 721 | Chongqing Gaoke Group Office | recovered | 23 | https://www.archdaily.com/987823/chongqing-gaoke-group-office-aedas | https://images.adsttc.com/media/images/6306/15bc/79c4/895b/df9f/dea5/large_jpg/not-ready-chongqing-gaoke-group-office-aedas_6.jpg?1661343229 |
| 726 | Lè Architecture | recovered | 15 | https://www.archdaily.com/902292/le-architecture-aedas | https://images.adsttc.com/media/images/5ba1/b4a8/f197/cc1b/4800/009f/large_jpg/1.jpg?1537324179 |
| 741 | Guanyun Qiantang City | recovered | 28 | https://www.archdaily.com/1026807/guanyun-qiantang-city-aedas | https://images.adsttc.com/media/images/67ab/7adb/dae3/4801/8ae8/897b/large_jpg/guanyun-qiantang-city-aedas_11.jpg?1739291383 |
| 746 | Quzhou Sports Park | recovered | 36 | https://www.archdaily.com/990244/quzhou-sports-park-mad-architects | https://images.adsttc.com/media/images/6342/f224/33b7/6e3d/3492/030e/large_jpg/quzhou-sports-park-mad-architects_36.jpg?1665331787 |
| 771 | Yohoo Museum | recovered | 17 | https://www.archdaily.com/1024957/yohoo-museum-aedas | https://images.adsttc.com/media/images/6763/8601/8d8d/7f01/87d6/bc7b/large_jpg/yohoo-museum-aedas_7.jpg?1734575701 |
| 781 | Nansha International Cruise Terminal Complex | recovered | 14 | https://www.archdaily.com/985774/nansha-international-cruise-terminal-complex-aedas | https://images.adsttc.com/media/images/62d9/4bf9/fbd1/0a44/f6e3/0bd7/large_jpg/not-ready-nansha-international-cruise-terminal-complex-aedas_6.jpg?1658407943 |
| 786 | ZGC International Innovation Center | recovered | 29 | https://www.archdaily.com/1017726/zgc-international-innovation-center-mad-architects | https://images.adsttc.com/media/images/666c/8b66/03ec/376b/eac2/a00f/large_jpg/zgc-international-innovation-center-mad-architects_6.jpg?1718389619 |
| 791 | Fenix Art Museum | recovered | 15 | https://www.archdaily.com/1030328/fenix-art-museum-mad-architects | https://images.adsttc.com/media/images/682c/9a38/82d8/2601/88bc/cacc/large_jpg/fenix-art-museum-mad-architects_4.jpg?1747753551 |
| 796 | Hyperlane | recovered | 19 | https://www.archdaily.com/1030231/hyperlane-aedas | https://images.adsttc.com/media/images/6826/9201/356c/7701/7ed7/215a/large_jpg/hyperlane-aedas_5.jpg?1747358220 |
| 801 | Конгресс-центр предпринимателей в Ябули | recovered | 23 | https://www.archdaily.com/980485/yabuli-entrepreneurs-congress-center-mad-architects | https://images.adsttc.com/media/images/625f/6b76/3e4b/3184/5f00/0028/large_jpg/feature.jpg?1650420589 |
| 806 | Музей научной фантастики в Чэнду | recovered | 12 | https://www.archdaily.com/1008749/chengdu-science-fiction-museum-zaha-hadid-architects | https://images.adsttc.com/media/images/6537/c6fa/7a42/3c30/6ff5/7a14/large_jpg/chengdu-science-fiction-museum-zaha-hadid-architects_9.jpg?1698154250 |
| 811 | Аэропорт Лишуй | recovered | 14 | https://www.archdaily.com/1038687/lishui-airport-mad-architects | https://images.adsttc.com/media/images/698b/ce4a/5706/8e05/9fe3/0cbd/large_jpg/lishui-airport-mad-architects_1.jpg?1770770009 |
| 816 | Музей цифрового искусства «Великий поход» | recovered | 30 | https://www.archdaily.com/1022354/long-march-cultural-digital-art-museum-china-ippr | https://images.adsttc.com/media/images/670d/9432/99d0/3a2e/cd7a/5e4e/large_jpg/long-march-cultural-digital-art-museum-china-ippr_6.jpg?1728943170 |
| 841 | Zhuhai Jinwan Civic Art Center | recovered | 44 | https://www.archdaily.com/1010787/zhuhai-jinwan-civic-art-center-zaha-hadid-architects | https://images.adsttc.com/media/images/6570/f16b/23c8/ee01/7cd2/7878/large_jpg/zhuhai-jinwan-civic-art-center-zaha-hadid-architects_4.jpg?1701900668 |

## Build validation

After regenerating the site data with `python /home/user/workspace/build_sohoarchtimes_catalog.py`:

- `posts_catalog.json`: 90 posts.
- `image_source_type == source_full`: 90 posts.
- `image_source_type == telegram_preview`: 0 posts.
- `slides_catalog.json`: 450 slides.
- Posts with non-5 image counts: 0.
- Build-compatible cache entries in `recovered_source_payloads.json`: 82.
