const { createApp, ref, computed, onMounted, nextTick } = Vue;

createApp({
    setup() {
        const photos = ref([]);
        const filter = ref('landscape'); // landscape, portrait
        
        const activeGallery = ref(null);
        const savedScrollY = ref(0); // 记录滚动位置
        
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

        onMounted(async () => {
            updateColCount();
            window.addEventListener('resize', updateColCount);
            
            try {
                // 读取 JSON 数据（附加时间戳防止 GitHub Pages 缓存死数据）
                const res = await fetch('data/photos.json?' + new Date().getTime());
                photos.value = await res.json();
            } catch(e) {
                console.error("加载摄影数据失败, 请确保已经使用 python 脚本上传了照片", e);
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
            
            // 等待 DOM 渲染出 dedicated-gallery 后再滚动
            nextTick(() => {
                const galleryEl = document.querySelector('.dedicated-gallery');
                if (galleryEl) {
                    const y = galleryEl.getBoundingClientRect().top + window.scrollY;
                    window.scrollTo({ top: y - 20, behavior: 'smooth' });
                } else {
                    window.scrollTo(0, 0);
                }
            });
        };

        const closeGallery = () => {
            activeGallery.value = null;
            
            // 等待 DOM 恢复为主列表后再恢复滚动位置
            nextTick(() => {
                window.scrollTo({ top: savedScrollY.value, behavior: 'instant' });
            });
        };

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

        return {
            photos, 
            filter, 
            groupedFeed, 
            itemDateFormatter,
            
            lightbox, 
            openLightbox, 
            closeLightbox,
            
            activeGallery, 
            openGallery, 
            closeGallery, 
            activeGalleryAllImages
        }
    }
}).mount('#app');
