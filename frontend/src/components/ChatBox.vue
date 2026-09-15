<template>
  <div class="chat-container">
    <div class="chat-header">
      <h4>💬 交易討論室</h4>
      <span class="refresh-hint">自動更新中...</span>
    </div>

    <div class="messages-area" ref="msgContainer">
      <div v-if="loading && messages.length === 0" class="loading-text">載入訊息中...</div>
      <div v-else-if="messages.length === 0" class="empty-text">尚無對話，快打個招呼吧！</div>

      <div
        v-for="msg in messages"
        :key="msg.id"
        class="message-row"
        :class="{ mine: msg.sender_id === currentUserId }"
      >
        <div class="bubble">
          <div class="sender" v-if="msg.sender_id !== currentUserId">{{ msg.sender_name }}</div>
          <div class="content">{{ msg.content }}</div>
          <div class="time">{{ formatTime(msg.created_at) }}</div>
        </div>
      </div>
    </div>

    <div v-if="!readOnly" class="input-area">
      <input
        v-model="newMessage"
        @keyup.enter="handleSend"
        type="text"
        placeholder="輸入訊息... (Enter 發送)"
        :disabled="sending"
      />
      <button @click="handleSend" :disabled="!newMessage.trim() || sending">發送</button>
    </div>

    <div v-else class="read-only-area">交易已完成，聊天功能已關閉</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { exchangesApi } from "@/api";

const props = defineProps({
  exchangeId: { type: String, required: true },
  currentUserId: { type: String, required: true },
  readOnly: { type: Boolean, default: false },
});

const messages = ref([]);
const newMessage = ref("");
const loading = ref(false);
const sending = ref(false);
const msgContainer = ref(null);
let pollingTimer = null;

// 格式化時間 HH:MM
const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

// 取得訊息
const fetchMessages = async () => {
  try {
    const res = await exchangesApi.getMessages(props.exchangeId);
    // 簡單判斷是否有新訊息才捲動，這裡簡化為每次都更新
    const shouldScroll = messages.value.length !== res.data.length;
    messages.value = res.data;

    if (shouldScroll) scrollToBottom();
  } catch (err) {
    console.error("Fetch messages failed", err);
  }
};

// 發送訊息
const handleSend = async () => {
  if (props.readOnly || !newMessage.value.trim() || sending.value) return;

  sending.value = true;
  try {
    await exchangesApi.sendMessage(props.exchangeId, newMessage.value);
    newMessage.value = "";
    await fetchMessages(); // 發送後立刻更新
    scrollToBottom();
  } catch {
    alert("訊息發送失敗");
  } finally {
    sending.value = false;
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
  }
};

onMounted(() => {
  loading.value = true;
  fetchMessages().then(() => (loading.value = false));

  // 每 3 秒輪詢一次新訊息
  if (!props.readOnly) {
    pollingTimer = setInterval(fetchMessages, 1000);
  }
});

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer);
});
</script>

<style scoped>
.chat-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  display: flex;
  flex-direction: column;
  height: 500px; /* 固定高度 */
  margin-top: 20px;
}

.chat-header {
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  background: #f9f9f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 8px 8px 0 0;
}
.chat-header h4 {
  margin: 0;
}
.refresh-hint {
  font-size: 0.8rem;
  color: #999;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background: #fdfdfd;
}

.message-row {
  display: flex;
  margin-bottom: 10px;
}
.message-row.mine {
  justify-content: flex-end;
}

.bubble {
  max-width: 70%;
  padding: 8px 12px;
  border-radius: 12px;
  position: relative;
  word-wrap: break-word;
}

.message-row .bubble {
  background: #e0e0e0;
  color: #333;
  border-bottom-left-radius: 0;
}
.message-row.mine .bubble {
  background: #4caf50;
  color: white;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 0;
}

.sender {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 2px;
}
.message-row.mine .sender {
  display: none;
} /* 自己不顯示名字 */

.time {
  font-size: 0.7rem;
  margin-top: 4px;
  text-align: right;
  opacity: 0.7;
}

.input-area {
  padding: 10px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}
.input-area input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
}
.input-area button {
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}
.input-area button:disabled {
  background: #ccc;
}
.read-only-area {
  padding: 15px;
  background: #f5f5f5;
  color: #888;
  text-align: center;
  border-top: 1px solid #eee;
  font-size: 0.9rem;
  border-radius: 0 0 8px 8px;
}
</style>
