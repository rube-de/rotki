<template>
  <progress-screen v-if="loading">
    <template #message>
      {{ t('trade_history.loading') }}
    </template>
    {{ t('trade_history.loading_subtitle') }}
  </progress-screen>
  <div v-else class="mt-8">
    <closed-trades @fetch="fetchTrades" />
  </div>
</template>

<script setup lang="ts">
import { get, useIntervalFn } from '@vueuse/core';
import { storeToRefs } from 'pinia';
import { onBeforeMount, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n-composable';
import ProgressScreen from '@/components/helper/ProgressScreen.vue';
import ClosedTrades from '@/components/history/ClosedTrades.vue';
import { setupStatusChecking } from '@/composables/common';
import { Section } from '@/store/const';
import { useTrades } from '@/store/history/trades';
import { useFrontendSettingsStore } from '@/store/settings/frontend';

const { refreshPeriod } = storeToRefs(useFrontendSettingsStore());
const { fetchTrades } = useTrades();

const period = get(refreshPeriod) * 60 * 1000;

const { pause, resume, isActive } = useIntervalFn(
  async () => {
    await fetchTrades(true);
  },
  period,
  { immediate: false }
);

onBeforeMount(async () => {
  await fetchTrades();

  if (period > 0) {
    resume();
  }
});

onUnmounted(() => {
  if (isActive) pause();
});

const { shouldShowLoadingScreen } = setupStatusChecking();
const loading = shouldShowLoadingScreen(Section.TRADES);

const { t } = useI18n();
</script>
