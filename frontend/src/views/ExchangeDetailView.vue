<template>
  <div class="page-container">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在讀取交換詳情...</p>
    </div>

    <div v-else-if="!exchange" class="error-state">
      <span class="icon">🚫</span>
      <h3>找不到此交換請求</h3>
      <button @click="router.push('/profile')" class="btn-back">返回個人頁面</button>
    </div>

    <div v-else class="detail-card">
      <div class="card-header">
        <div class="header-left">
          <h1>交換詳情</h1>
          <span class="id-tag">#{{ exchange.id.slice(0, 8) }}</span>
        </div>
        <div class="status-badge" :class="exchange.status">
          {{ translateStatus(exchange.status) }}
        </div>
      </div>

      <div class="exchange-visual">
        <div class="party-col">
          <div class="role-label">👤 對方提供</div>
          <div class="item-card-mini" :class="{ empty: !theirItem }">
            <template v-if="theirItem">
              <div class="img-wrapper">
                <img
                  :src="
                    theirItem.cover_image ||
                    theirItem.image_url ||
                    'https://via.placeholder.com/150'
                  "
                />
              </div>
              <p class="item-title">{{ theirItem.title }}</p>
            </template>
            <template v-else>
              <span class="gift-icon">🎁</span>
              <p class="item-title">索取</p>
            </template>
          </div>
        </div>

        <div class="exchange-icon">
          <span class="arrow">⇄</span>
        </div>

        <div class="party-col">
          <div class="role-label self">👤 我提供</div>
          <div class="item-card-mini" :class="{ empty: !myItem }">
            <template v-if="myItem">
              <div class="img-wrapper">
                <img
                  :src="myItem.cover_image || myItem.image_url || 'https://via.placeholder.com/150'"
                />
              </div>
              <p class="item-title">{{ myItem.title }}</p>
            </template>
            <template v-else>
              <span class="gift-icon">🎁</span>
              <p class="item-title">索取</p>
            </template>
          </div>
        </div>
      </div>

      <div class="message-section">
        <div class="quote-box">
          <span class="quote-icon">❝</span>
          <p class="message-content">{{ exchange.message || "（對方未留下訊息）" }}</p>
          <div class="message-meta">
            <span>請求時間：{{ formatDate(exchange.created_at) }}</span>
          </div>
        </div>
      </div>

      <div v-if="exchange.status === 'accepted'" class="active-deal-dashboard">
        <div class="dashboard-header">
          <h3>交易進行中</h3>
          <p>請約定時間地點並完成交換。</p>
        </div>

        <div class="location-card">
          <div class="loc-icon">📍</div>
          <div class="loc-info">
            <template v-if="exchange.deal_info?.meetup_location">
              <strong>{{ exchange.deal_info.meetup_location.name }}</strong>
              <span class="address">{{
                exchange.deal_info.meetup_location.address || "無詳細地址"
              }}</span>
            </template>
            <template v-else>
              <span class="warning">尚未約定面交地點</span>
              <span class="sub-warning">請點擊右側按鈕設定地點</span>
            </template>
          </div>
          <button v-if="!myConfirmed" @click="openLocationModal" class="btn-edit-loc">
            {{ exchange.deal_info?.meetup_location ? "修改地點" : "設定地點" }}
          </button>
        </div>

        <div class="confirmation-status">
          <div class="status-step" :class="{ active: myConfirmed }">
            <div class="step-circle">{{ myConfirmed ? "✓" : "1" }}</div>
            <span>我方確認</span>
          </div>
          <div class="step-line"></div>
          <div class="status-step" :class="{ active: partnerConfirmed }">
            <div class="step-circle">{{ partnerConfirmed ? "✓" : "2" }}</div>
            <span>對方確認</span>
          </div>
        </div>

        <div class="dashboard-actions">
          <button
            v-if="!myConfirmed"
            @click="handleConfirm"
            class="btn-confirm-deal"
            :disabled="isSubmitting"
          >
            確認完成交易
          </button>

          <div v-else class="waiting-msg">
            <button @click="handleRevokeConfirm" class="btn-revoke" :disabled="isSubmitting">
              ↺ 取消確認
            </button>
            <span v-if="!partnerConfirmed">已確認，等待對方...</span>
          </div>
        </div>
      </div>

      <div v-if="exchange.status === 'completed'" class="success-banner">
        <h3>交易完成！</h3>
        <p>感謝您的參與，物品交換已順利結束。</p>
      </div>

      <div
        v-if="['accepted', 'completed'].includes(exchange.status) && authStore.user"
        class="chat-wrapper"
      >
        <ChatBox
          :exchange-id="exchange.id"
          :current-user-id="authStore.user.id"
          :read-only="exchange.status === 'completed'"
        />
      </div>

      <div class="action-footer">
        <div v-if="isOwner && exchange.status === 'pending'" class="owner-actions">
          <button @click="handleReject" class="btn-reject" :disabled="isSubmitting">✕ 拒絕</button>
          <button @click="handleAccept" class="btn-accept" :disabled="isSubmitting">
            ✓ 接受交換
          </button>
        </div>

        <div v-if="canCancel" class="cancel-wrapper">
          <div class="divider"></div>

          <button @click="handleCancel" class="btn-withdraw" :disabled="isSubmitting">
            <span class="icon">🚫</span>
            {{ exchange.status === "pending" ? "撤回交換請求" : "終止交易" }}
          </button>

          <p v-if="exchange.status === 'accepted'" class="cancel-hint">
            取消後交易將終止，物品將自動重新上架。
          </p>
        </div>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="showLocationModal" class="modal-overlay" @click.self="showLocationModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>{{ exchange.deal_info?.meetup_location ? "更改" : "設定" }}面交地點</h3>
            <button class="btn-close" @click="showLocationModal = false">✕</button>
          </div>
          <div class="modal-body">
            <p class="modal-desc">請選擇一個方便面交的地點：</p>

            <div class="location-list">
              <div
                v-for="loc in locations"
                :key="loc.id"
                class="location-option"
                :class="{ selected: newLocationId === loc.id }"
                @click="newLocationId = loc.id"
              >
                <div class="radio-indicator"></div>
                <div class="loc-text">
                  <span class="loc-name">{{ loc.name }}</span>
                  <span class="loc-addr">{{ loc.address }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showLocationModal = false" class="btn-cancel">取消</button>
            <button
              @click="handleUpdateLocation"
              class="btn-confirm"
              :disabled="!newLocationId || isSubmitting"
            >
              確認設定
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { exchangesApi } from "@/api";
import { useAuthStore } from "@/stores/auth";
import ChatBox from "@/components/ChatBox.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const loading = ref(true);
const exchange = ref(null);
const locations = ref([]);
const showLocationModal = ref(false);
const newLocationId = ref("");
const isSubmitting = ref(false);

const currentUserId = computed(() => authStore.user?.id);
const isOwner = computed(() => exchange.value?.owner?.user_id === currentUserId.value);
const isRequester = computed(() => exchange.value?.requester?.user_id === currentUserId.value);

const theirItem = computed(() =>
  isOwner.value ? exchange.value?.offered_item : exchange.value?.target_item
);
const myItem = computed(() =>
  isOwner.value ? exchange.value?.target_item : exchange.value?.offered_item
);

const myConfirmed = computed(() => {
  if (!exchange.value) return false;
  return isOwner.value ? exchange.value.owner_confirmed : exchange.value.requester_confirmed;
});

const partnerConfirmed = computed(() => {
  if (!exchange.value) return false;
  return isOwner.value ? exchange.value.requester_confirmed : exchange.value.owner_confirmed;
});

const canCancel = computed(() => {
  if (!exchange.value) return false;
  const status = exchange.value.status;
  if (status === "pending" && isRequester.value) return true;
  if (status === "accepted") return true;
  return false;
});

const fetchDetail = async () => {
  loading.value = true;
  try {
    const res = await exchangesApi.getExchangeDetail(route.params.id);
    exchange.value = res.data;
  } catch (err) {
    console.error(err);
    alert("無法載入詳情");
    router.push("/profile");
  } finally {
    loading.value = false;
  }
};

// --- 修改：接受交換邏輯 ---
// 不再開啟 Modal，直接確認後送出請求 (不帶地點 ID)
const handleAccept = async () => {
  if (!confirm("確定要接受此交換請求嗎？")) return;

  isSubmitting.value = true;
  try {
    // 這裡只傳 action，不傳 location
    await exchangesApi.updateExchangeStatus(exchange.value.id, {
      action: "accept",
    });
    // 重新整理資料，狀態會變更為 accepted
    await fetchDetail();
  } catch (err) {
    console.error(err);
    alert("操作失敗，請稍後再試");
  } finally {
    isSubmitting.value = false;
  }
};

const handleReject = async () => {
  if (!confirm("確定要拒絕此交換嗎？")) return;
  performAction(() => exchangesApi.updateExchangeStatus(exchange.value.id, { action: "reject" }));
};

const handleConfirm = async () => {
  if (!confirm("確認已完成交換？")) return;
  performAction(() => exchangesApi.confirmExchange(exchange.value.id));
};

const handleRevokeConfirm = async () => {
  if (!confirm("要取消確認狀態嗎？")) return;
  performAction(() => exchangesApi.confirmExchange(exchange.value.id, { action: "revoke" }));
};

const handleCancel = async () => {
  if (!confirm("確定要取消/撤回此交易嗎？")) return;
  performAction(() => exchangesApi.cancelExchange(exchange.value.id));
};

const performAction = async (fn) => {
  isSubmitting.value = true;
  try {
    await fn();
    fetchDetail();
  } catch {
    alert("操作失敗");
  } finally {
    isSubmitting.value = false;
  }
};

// --- 修改：地點選擇邏輯 ---
const openLocationModal = async () => {
  // 如果還沒載入過地點，先載入
  if (locations.value.length === 0) {
    try {
      const res = await exchangesApi.getLocations();
      locations.value = res.data;
    } catch {
      alert("無法載入地點列表");
      return;
    }
  }

  // 設定預設值
  if (exchange.value.deal_info?.meetup_location?.id) {
    newLocationId.value = exchange.value.deal_info.meetup_location.id;
  } else {
    newLocationId.value = ""; // 重置
  }

  showLocationModal.value = true;
};

const handleUpdateLocation = async () => {
  if (!newLocationId.value) return;

  isSubmitting.value = true;
  try {
    await exchangesApi.updateLocation(exchange.value.id, newLocationId.value);
    showLocationModal.value = false;
    fetchDetail();
  } catch {
    alert("更新地點失敗");
  } finally {
    isSubmitting.value = false;
  }
};

const translateStatus = (s) =>
  ({
    pending: "等待中",
    accepted: "交易中",
    rejected: "已拒絕",
    completed: "已完成",
    cancelled: "已取消",
  }[s] || s);

const formatDate = (d) => (d ? new Date(d).toLocaleString() : "");

onMounted(fetchDetail);
</script>

<style scoped>
.page-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
}

/* 狀態頁 */
.loading-state,
.error-state {
  text-align: center;
  padding: 60px 0;
  color: #64748b;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #eee;
  border-top-color: #42b983;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.error-state .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 10px;
}

/* 主卡片 */
.detail-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  padding: 40px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 20px;
}
.header-left h1 {
  margin: 0;
  color: #1e293b;
  font-size: 1.8rem;
}
.id-tag {
  color: #94a3b8;
  font-size: 0.9rem;
  font-family: monospace;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 0.95rem;
}
.status-badge.pending {
  background: #fff7ed;
  color: #ea580c;
}
.status-badge.accepted {
  background: #eff6ff;
  color: #2563eb;
}
.status-badge.completed {
  background: #ecfdf5;
  color: #059669;
}
.status-badge.rejected,
.status-badge.cancelled {
  background: #fef2f2;
  color: #dc2626;
}

/* 交換視覺化 */
.exchange-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  margin-bottom: 40px;
}
.party-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 250px;
}
.role-label {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 10px;
  font-weight: 600;
}
.role-label.self {
  color: #42b983;
}

.item-card-mini {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 15px;
  text-align: center;
  background: #fff;
  transition: transform 0.2s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}
.item-card-mini:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.05);
}
.item-card-mini.empty {
  background: #f8fafc;
  border-style: dashed;
}

.img-wrapper {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 10px;
  background: #f1f5f9;
}
.img-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.gift-icon {
  font-size: 3rem;
  display: block;
  margin: 20px 0;
  opacity: 0.5;
}
.item-title {
  font-weight: 600;
  color: #334155;
  margin: 0;
  font-size: 1rem;
}
.exchange-icon .arrow {
  font-size: 2rem;
  color: #cbd5e0;
}

/* 訊息區 */
.message-section {
  margin-bottom: 30px;
}
.quote-box {
  background: #f8fafc;
  border-left: 4px solid #42b983;
  padding: 20px 20px 20px 40px;
  border-radius: 0 8px 8px 0;
  position: relative;
}
.quote-icon {
  position: absolute;
  left: 10px;
  top: 10px;
  font-size: 2rem;
  color: #cbd5e0;
  line-height: 1;
}
.message-content {
  color: #334155;
  font-size: 1.05rem;
  line-height: 1.6;
  margin: 0 0 10px 0;
}
.message-meta {
  font-size: 0.85rem;
  color: #94a3b8;
  text-align: right;
}

/* 交易儀表板 */
.active-deal-dashboard {
  background: linear-gradient(to right, #eff6ff, #f8fafc);
  border: 1px solid #bfdbfe;
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
}
.dashboard-header {
  text-align: center;
  margin-bottom: 25px;
}
.dashboard-header h3 {
  color: #1e40af;
  margin: 0 0 5px;
}
.dashboard-header p {
  color: #60a5fa;
  margin: 0;
  font-size: 0.95rem;
}

.location-card {
  background: white;
  border-radius: 10px;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  margin-bottom: 25px;
}
.loc-icon {
  font-size: 1.5rem;
}
.loc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.loc-info strong {
  color: #1e293b;
}
.loc-info .address {
  font-size: 0.9rem;
  color: #64748b;
}
.loc-info .warning {
  color: #f59e0b;
  font-weight: bold;
}
.loc-info .sub-warning {
  font-size: 0.8rem;
  color: #94a3b8;
}
.btn-edit-loc {
  border: 1px solid #cbd5e0;
  background: white;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: #64748b;
  font-size: 0.9rem;
  transition: 0.2s;
}
.btn-edit-loc:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.confirmation-status {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 25px;
}
.status-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  opacity: 0.5;
}
.status-step.active {
  opacity: 1;
  color: #059669;
}
.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
}
.status-step.active .step-circle {
  background: #059669;
}
.step-line {
  width: 50px;
  height: 2px;
  background: #e2e8f0;
}

.dashboard-actions {
  display: flex;
  justify-content: center;
}
.btn-confirm-deal {
  background: #2563eb;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
}
.btn-confirm-deal:hover {
  background: #1d4ed8;
}
.waiting-msg {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #059669;
  font-weight: bold;
}
.btn-revoke {
  background: white;
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}

/* 底部按鈕 */
.action-footer {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  margin-top: 40px;
  border-top: 1px solid #f1f5f9;
  padding-top: 30px;
}
.owner-actions {
  display: flex;
  gap: 20px;
}
.btn-accept {
  background: #42b983;
  color: white;
  border: none;
  padding: 10px 30px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.btn-reject {
  background: white;
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 10px 30px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
.cancel-wrapper {
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.divider {
  height: 1px;
  background-color: #f1f5f9;
  width: 80%;
  margin-bottom: 10px;
}

.btn-withdraw {
  background-color: white;
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.btn-withdraw:hover:not(:disabled) {
  background-color: #fef2f2;
  border-color: #dc2626;
  color: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
}

.btn-withdraw:active:not(:disabled) {
  transform: translateY(0);
}

.btn-withdraw:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-withdraw .icon {
  font-size: 1.1rem;
}

.cancel-hint {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
  text-align: center;
}
.success-banner {
  background: #ecfdf5;
  color: #065f46;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
}

/* Modal & RWD */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-card {
  background: white;
  width: 90%;
  max-width: 500px;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  max-height: 90vh; /* 防止內容過長 */
  display: flex;
  flex-direction: column;
}
.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-body {
  padding: 25px;
  overflow-y: auto; /* 內容多時可捲動 */
}
.modal-desc {
  color: #64748b;
  margin-bottom: 15px;
  font-size: 0.95rem;
}

.modal-footer {
  padding: 15px 25px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
}

/* 優化後的 Location 選單樣式 
  使用 Grid 或 Flex 列表取代 Select
*/
.location-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.location-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.location-option:hover {
  background: #f8fafc;
  border-color: #cbd5e0;
}

.location-option.selected {
  border-color: #42b983;
  background: #ecfdf5;
}

/* 模擬 Radio 按鈕 */
.radio-indicator {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #cbd5e0;
  flex-shrink: 0;
  position: relative;
}

.location-option.selected .radio-indicator {
  border-color: #42b983;
}
.location-option.selected .radio-indicator::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  background: #42b983;
  border-radius: 50%;
}

.loc-text {
  display: flex;
  flex-direction: column;
}

.loc-name {
  font-weight: 600;
  color: #334155;
  font-size: 1rem;
}

.loc-addr {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 2px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #94a3b8;
}
.btn-cancel {
  background: white;
  border: 1px solid #cbd5e0;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
}
.btn-confirm {
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}
.btn-confirm:disabled {
  background: #a7f3d0;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .exchange-visual {
    flex-direction: column;
    gap: 15px;
  }
  .exchange-icon .arrow {
    transform: rotate(90deg);
  }
  .party-col {
    width: 100%;
    max-width: none;
  }
  .card-header {
    flex-direction: column;
    gap: 10px;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
