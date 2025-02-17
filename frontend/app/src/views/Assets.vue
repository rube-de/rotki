﻿<template>
  <v-container class="pb-12">
    <v-row class="mt-12" align="center" justify="space-between">
      <v-col>
        <v-row align="center">
          <v-col cols="auto">
            <asset-icon :identifier="identifier" size="48px" />
          </v-col>
          <v-col class="d-flex flex-column" cols="auto">
            <span class="text-h5 font-weight-medium">{{ symbol }}</span>
            <span class="text-subtitle-2 text--secondary">
              {{ name }}
            </span>
          </v-col>
          <v-col cols="auto">
            <v-btn icon :to="editRoute">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="auto">
        <v-row align="center">
          <v-col cols="auto">
            <div class="text-subtitle-2">{{ t('assets.ignore') }}</div>
          </v-col>
          <v-col>
            <v-switch :input-value="isIgnored" @change="toggleIgnoreAsset" />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <asset-value-row class="mt-8" :identifier="identifier" :symbol="symbol" />
    <asset-amount-and-value-over-time
      v-if="premium"
      class="mt-8"
      :asset="identifier"
    />
    <asset-locations class="mt-8" :identifier="identifier" />
  </v-container>
</template>

<script setup lang="ts">
import { get } from '@vueuse/core';
import { computed, toRefs } from 'vue';
import { useI18n } from 'vue-i18n-composable';
import { RawLocation } from 'vue-router';
import AssetLocations from '@/components/assets/AssetLocations.vue';
import AssetValueRow from '@/components/assets/AssetValueRow.vue';
import { getPremium } from '@/composables/session';
import { AssetAmountAndValueOverTime } from '@/premium/premium';
import { Routes } from '@/router/routes';
import { useIgnoredAssetsStore } from '@/store/assets/ignored';
import { useAssetInfoRetrieval } from '@/store/assets/retrieval';

const props = defineProps({
  identifier: { required: true, type: String }
});

const { identifier } = toRefs(props);
const { isAssetIgnored, ignoreAsset, unignoreAsset } = useIgnoredAssetsStore();

const isIgnored = isAssetIgnored(identifier);

const toggleIgnoreAsset = async () => {
  const id = get(identifier);
  if (get(isIgnored)) {
    await unignoreAsset(id);
  } else {
    await ignoreAsset(id);
  }
};

const editRoute = computed<RawLocation>(() => {
  return {
    path: Routes.ASSET_MANAGER.route,
    query: {
      id: get(identifier)
    }
  };
});

const premium = getPremium();

const { assetName, assetSymbol } = useAssetInfoRetrieval();

const name = computed<string>(() => {
  return get(assetName(get(identifier)));
});

const symbol = computed<string>(() => {
  return get(assetSymbol(get(identifier)));
});

const { t } = useI18n();
</script>
