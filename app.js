const { createApp, ref, computed, onMounted, nextTick, watch } = Vue;

createApp({
    setup() {
        const OSS_DOMAIN = "https://www-seikai.oss-cn-hangzhou.aliyuncs.com/lens/";
        const dpr = ref(window.devicePixelRatio || 1);
        const winW = ref(window.innerWidth);
        const winH = ref(window.innerHeight);

        const toOSS = (url, type) => {
            if (!url || url.startsWith('http')) return url;
            let fullUrl = OSS_DOMAIN + (url.startsWith('/') ? url.slice(1) : url);
            
            let screenW = winW.value;
            let r = dpr.value;
            
            if (type === 'thumb_L') {
                let targetHeight = 280;
                if (screenW < 480) targetHeight = 80;
                else if (screenW < 768) targetHeight = 140;
                else if (screenW < 1024) targetHeight = 220;
                
                const reqH = Math.ceil(targetHeight * r / 100) * 100;
                const reqW = Math.ceil(screenW * r / 100) * 100;
                return fullUrl + `?x-oss-process=image/resize,m_lfit,w_${reqW},h_${reqH}`;
            } else if (type === 'thumb_P') {
                const cols = screenW < 768 ? 1 : (screenW < 1024 ? 2 : 3);
                let cellW = screenW < 900 ? screenW / cols : 300;
                const thumbW = Math.ceil((cellW * 2) * r / 100) * 100;
                return fullUrl + `?x-oss-process=image/resize,m_fill,w_${thumbW},h_${thumbW}`;
            } else if (type === 'disp') {
                const screenH = winH.value;
                const dispW = Math.ceil(screenW * r / 100) * 100;
                const dispH = Math.ceil(screenH * r / 100) * 100;
                return fullUrl + `?x-oss-process=image/resize,m_lfit,w_${dispW},h_${dispH}`;
            }
            return fullUrl;
        };

        const dynamicImages = computed(() => {
            const w = winW.value;
            const r = dpr.value;
            
            let avatarW = Math.max(60, Math.min(140, w * 0.11666));
            let avatarReqW = Math.ceil(avatarW * r / 100) * 100;
            if (avatarReqW < 100) avatarReqW = 100;

            let qrReqW = Math.ceil(150 * r / 100) * 100;
            
            let aboutW = Math.min(600, w - 40); 
            let aboutReqW = Math.ceil(aboutW * r / 100) * 100;

            return {
                avatar: `${OSS_DOMAIN}public/avatar.webp?x-oss-process=image/resize,w_${avatarReqW}`,
                qrcode: `${OSS_DOMAIN}public/qrcode.webp?x-oss-process=image/resize,w_${qrReqW}`,
                xiaohongshu: `${OSS_DOMAIN}public/xiaohongshu-qrcode.webp?x-oss-process=image/resize,w_${qrReqW}`,
                aboutMe: `${OSS_DOMAIN}public/about_me.webp?x-oss-process=image/resize,w_${aboutReqW}`,
                logo: `${OSS_DOMAIN}public/logo.png`
            };
        });
        const photos = ref([]);
        const masterpieces = ref([]);
        const filter = ref('landscape'); // landscape, portrait
        const currentPage = ref('home'); // home, masterpieces, gear, about
        const isHeroLoaded = ref(false);
        
        const activeGallery = ref(null);
        const savedScrollY = ref(0); // 记录滚动位置
        const isScrolled = ref(false); // 是否发生滚动
        
        const lightbox = ref({
            isOpen: false,
            url: '',
            item: null
        });

        // 响应式计算瀑布流列数
        const colCount = ref(3);
        const updateColCount = () => {
            const width = window.innerWidth;
            if (width <= 768) {
                colCount.value = 2;
            } else {
                // PC端：根据宽度自适应计算，还原之前的 auto 220px 计算逻辑，支持 4K 大屏多列显示
                const containerWidth = Math.min(1800, width * 0.9);
                let n = Math.floor((containerWidth + 16) / 236);
                colCount.value = Math.max(1, n);
            }
        };

        // 视差滚动特效及头部透明度切换
        const getStickyThreshold = () => {
            const heroEl = document.querySelector('.hero');
            const headerEl = document.querySelector('.top-header');
            if (heroEl && headerEl) {
                return heroEl.offsetHeight - headerEl.offsetHeight;
            }
            return 300; // fallback
        };

        let ticking = false;
        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const y = window.scrollY;
                    isScrolled.value = y > 50;
                    
                    if (!activeGallery.value) { // 仅在首页展示开屏时计算视差
                        if (y < window.innerHeight) {
                            document.documentElement.style.setProperty('--parallax-y', `${y * 0.5}px`);
                        }
                    }

                    // 动态计算毛玻璃过渡比例
                    const threshold = getStickyThreshold();
                    let progress = y / threshold;
                    if (progress < 0) progress = 0;
                    if (progress > 1) progress = 1;
                    document.documentElement.style.setProperty('--nav-blur-progress', progress);

                    ticking = false;
                });
                ticking = true;
            }
        };

        onMounted(async () => {
            updateColCount();
            
            // 动态加载高清头图 (Blur-Up)
            const loadHighResHero = () => {
                // 计算实际需要的物理像素宽度，按 100px 向上取整以提高 CDN 命中率，最大不超过 3840
                let targetWidth = Math.ceil((window.innerWidth * (window.devicePixelRatio || 1)) / 100) * 100;
                if (targetWidth > 3840) targetWidth = 3840;
                
                const highResUrl = `https://www-seikai.oss-cn-hangzhou.aliyuncs.com/lens/public/hero-bg-4k.webp?x-oss-process=image/resize,w_${targetWidth}`;
                
                // 仅当 URL 改变时才去重新加载
                const currentUrl = document.documentElement.style.getPropertyValue('--hero-bg-highres');
                if (currentUrl.includes(highResUrl)) {
                    isHeroLoaded.value = true;
                    return;
                }
                
                const img = new Image();
                img.onload = () => {
                    document.documentElement.style.setProperty('--hero-bg-highres', `url('${highResUrl}')`);
                    isHeroLoaded.value = true;
                };
                img.src = highResUrl;
            };
            
            setTimeout(loadHighResHero, 100);

            let resizeTimer;
            window.addEventListener('resize', () => {
                winW.value = window.innerWidth;
                winH.value = window.innerHeight;
                dpr.value = window.devicePixelRatio || 1;
                updateColCount();
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(loadHighResHero, 500);
            });
            window.addEventListener('scroll', handleScroll, { passive: true });
            


            try {
                const res = await fetch('data/photos.json?' + new Date().getTime());
                let rawPhotos = await res.json();
                
                rawPhotos.forEach(p => {
                    if (p.type === 'gallery' && p.layout) {
                        for (let key in p.layout) {
                            if (p.layout[key].thumbnail) p.layout[key].thumbnail = toOSS(p.layout[key].thumbnail, 'thumb_P');
                            if (p.layout[key].display) p.layout[key].display = toOSS(p.layout[key].display, 'disp');
                        }
                        if (p.others) {
                            p.others.forEach(o => {
                                if (o.thumbnail) o.thumbnail = toOSS(o.thumbnail, 'thumb_P');
                                if (o.display) o.display = toOSS(o.display, 'disp');
                            });
                        }
                    } else if (p.type === 'single') {
                        if (p.thumbnail) p.thumbnail = toOSS(p.thumbnail, 'thumb_L');
                        if (p.display) p.display = toOSS(p.display, 'disp');
                    }
                });
                photos.value = rawPhotos;
            } catch(e) {
                console.error("加载摄影数据失败, 请确保已经使用 python 脚本上传了照片", e);
            }

            try {
                const resM = await fetch('data/masterpieces.json?' + new Date().getTime());
                let rawMasterpieces = await resM.json();
                rawMasterpieces.forEach(m => {
                    if (m.url) m.url = toOSS(m.url, 'disp');
                });
                masterpieces.value = rawMasterpieces;
            } catch(e) {
                console.error("加载代表作数据失败", e);
            }
        });

        // 过滤数据逻辑
        const filteredPhotos = computed(() => {
            const targetCategory = filter.value === 'landscape' ? 'L' : 'P';
            return photos.value.filter(p => p.category === targetCategory);
        });

        const groupedFeed = computed(() => {
            let feed = [];
            let currentJustified = [];
            
            filteredPhotos.value.forEach(p => {
                if (p.type === 'single') {
                    currentJustified.push(p);
                } else {
                    if (currentJustified.length > 0) {
                        feed.push({ type: 'justified', items: currentJustified });
                        currentJustified = [];
                    }
                    feed.push({ type: 'gallery', item: p });
                }
            });
            // 扫尾工作
            if (currentJustified.length > 0) {
                feed.push({ type: 'justified', items: currentJustified });
            }
            return feed;
        });

        // 格式化日期：将 2026-06-10 格式化为漂亮的英文月份展示
        const itemDateFormatter = (dateStr) => {
            if(!dateStr) return '';
            const d = new Date(dateStr);
            if(isNaN(d)) return dateStr;
            // 例如：JUN 10, 2026
            return d.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            }).toUpperCase();
        };

        // 灯箱逻辑
        const openLightbox = (url, item) => {
            lightbox.value = { isOpen: true, url, item };
            // 禁止底层滚动
            document.body.style.overflow = 'hidden';
        };

        const closeLightbox = () => {
            lightbox.value.isOpen = false;
            document.body.style.overflow = '';
        };

        // 组图全屏界面逻辑
        const openGallery = (item) => {
            savedScrollY.value = window.scrollY; // 记录当前滚动位置
            activeGallery.value = item;
            
            nextTick(() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        };

        const closeGallery = () => {
            activeGallery.value = null;
            
            // 等待 DOM 恢复为主列表后再恢复滚动位置
            nextTick(() => {
                window.scrollTo({ top: savedScrollY.value, behavior: 'instant' });
            });
        };

        const savedScroll = {
            landscape: 0,
            portrait: 0
        };

        watch(filter, (newVal, oldVal) => {
            if (currentPage.value === 'home') {
                const currentY = window.scrollY;
                savedScroll[oldVal] = currentY;
                const threshold = getStickyThreshold();

                if (currentY < threshold) {
                    savedScroll[newVal] = currentY;
                } else {
                    if (savedScroll[newVal] < threshold) {
                        savedScroll[newVal] = threshold;
                    }
                }
                
                nextTick(() => {
                    window.scrollTo({ top: savedScroll[newVal], behavior: 'instant' });
                });
            }
        });

        watch([currentPage, activeGallery], () => {
            const isSubpage = currentPage.value !== 'home' || activeGallery.value;
            if (isSubpage) {
                document.body.classList.add('is-subpage');
            } else {
                document.body.classList.remove('is-subpage');
            }
        }, { immediate: true });

        watch(currentPage, (newVal, oldVal) => {
            if (oldVal === 'home') {
                savedScroll[filter.value] = window.scrollY;
            }
            
            nextTick(() => {
                if (newVal === 'home') {
                    window.scrollTo({ top: savedScroll[filter.value], behavior: 'instant' });
                } else {
                    window.scrollTo(0, 0);
                }
            });
        });

        // 获取当前组图专属界面下的所有大图数组
        const activeGalleryAllImages = computed(() => {
            if(!activeGallery.value) return [];
            const item = activeGallery.value;
            let arr = [];
            
            // 按照 1+5 的顺序先加入
            const req = ['cover', 'grid_1', 'grid_2', 'grid_3', 'grid_4', 'grid_5'];
            req.forEach(k => {
                if(item.layout && item.layout[k]) {
                    arr.push(item.layout[k].display);
                }
            });
            
            // 再加入剩下的 others
            if(item.others) {
                item.others.forEach(o => arr.push(o.display));
            }
            return arr;
        });

        const sortedMasterpieces = computed(() => {
            return [...masterpieces.value].sort((a, b) => new Date(b.date) - new Date(a.date));
        });

        const activeMIndex = ref(0);
        const activeMasterpiece = computed(() => sortedMasterpieces.value[activeMIndex.value]);

        const prevMasterpiece = () => {
            if (activeMIndex.value > 0) activeMIndex.value--;
        };
        const nextMasterpiece = () => {
            if (activeMIndex.value < sortedMasterpieces.value.length - 1) activeMIndex.value++;
        };

        const thumbContainer = ref(null);
        
        const centerThumbnail = (index) => {
            nextTick(() => {
                if (!thumbContainer.value) return;
                const container = thumbContainer.value;
                const activeThumb = container.children[index];
                if (activeThumb) {
                    const containerRect = container.getBoundingClientRect();
                    const thumbRect = activeThumb.getBoundingClientRect();
                    const thumbCenter = thumbRect.left + (thumbRect.width / 2);
                    const containerCenter = containerRect.left + (containerRect.width / 2);
                    const offset = thumbCenter - containerCenter;
                    container.scrollBy({ left: offset, behavior: 'smooth' });
                }
            });
        };

        watch(activeMIndex, (newVal) => {
            centerThumbnail(newVal);
        });

        return {
            photos, 
            masterpieces: sortedMasterpieces,
            activeMIndex,
            activeMasterpiece,
            prevMasterpiece,
            nextMasterpiece,
            thumbContainer,
            filter, 
            groupedFeed, 
            itemDateFormatter,
            
            lightbox, 
            openLightbox, 
            closeLightbox,

            dynamicImages,
            filter,
            currentPage,
            isHeroLoaded,
            isScrolled,
            activeGallery, 
            openGallery, 
            closeGallery, 
            activeGalleryAllImages
        }
    }
}).mount('#app');
