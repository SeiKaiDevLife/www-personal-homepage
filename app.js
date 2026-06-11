const { createApp, ref, computed, onMounted } = Vue;

createApp({
    setup() {
        const photos = ref([]);
        const filter = ref('landscape'); // landscape, portrait
        
        const activeGallery = ref(null);
        
        const lightbox = ref({
            isOpen: false,
            url: '',
            item: null
        });

        onMounted(async () => {
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

        // 将数据按要求进行打包，相邻的单图放入同一个瀑布流 block，组图独立为一个 block
        const groupedFeed = computed(() => {
            let feed = [];
            let currentMasonry = [];
            
            filteredPhotos.value.forEach(p => {
                if (p.type === 'single') {
                    currentMasonry.push(p);
                } else {
                    if (currentMasonry.length > 0) {
                        feed.push({ type: 'masonry', items: currentMasonry });
                        currentMasonry = [];
                    }
                    feed.push({ type: 'gallery', item: p });
                }
            });
            // 扫尾工作
            if (currentMasonry.length > 0) {
                feed.push({ type: 'masonry', items: currentMasonry });
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
            activeGallery.value = item;
            window.scrollTo(0, 0); // 回到顶部
        };

        const closeGallery = () => {
            activeGallery.value = null;
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
