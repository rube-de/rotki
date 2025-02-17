import { mount, Wrapper } from '@vue/test-utils';
import { set } from '@vueuse/core';
import {
  createPinia,
  PiniaVuePlugin,
  setActivePinia,
  storeToRefs
} from 'pinia';
import Vue from 'vue';
import Vuetify from 'vuetify';
import { BackupApi } from '@/services/backup/backup-api';
import { BalancesApi } from '@/services/balances/balances-api';
import { api } from '@/services/rotkehlchen-api';
import { usePremiumStore } from '@/store/session/premium';
import UserSecuritySettings from '@/views/settings/UserSecuritySettings.vue';
import { stub } from '../../../common/utils';
import '../../i18n';

vi.spyOn(api, 'backups', 'get').mockReturnValue(
  stub<BackupApi>({
    info: vi.fn()
  })
);

vi.spyOn(api, 'balances', 'get').mockReturnValue(
  stub<BalancesApi>({
    getPriceCache: vi.fn().mockResolvedValue([])
  })
);
vi.mock('vue', async () => {
  const mod = await vi.importActual<typeof import('vue')>('vue');
  return {
    ...mod,
    useListeners: vi.fn(),
    useAttrs: vi.fn()
  };
});

Vue.use(Vuetify);
Vue.use(PiniaVuePlugin);

describe('UserSecuritySettings.vue', () => {
  let wrapper: Wrapper<any>;

  function createWrapper() {
    const vuetify = new Vuetify();
    const pinia = createPinia();
    setActivePinia(pinia);
    return mount(UserSecuritySettings, {
      pinia,
      vuetify,
      stubs: [
        'v-tooltip',
        'card-title',
        'asset-select',
        'asset-update',
        'confirm-dialog',
        'data-table',
        'card'
      ]
    });
  }

  beforeEach(() => {
    wrapper = createWrapper();
  });

  test('displays no warning by default', async () => {
    expect(wrapper.find('[data-cy=premium-warning]').exists()).toBe(false);
  });

  test('displays warning if premium sync enabled', async () => {
    const { premiumSync } = storeToRefs(usePremiumStore());
    set(premiumSync, true);
    await wrapper.vm.$nextTick();
    expect(wrapper.find('[data-cy=premium-warning]').exists()).toBe(true);
  });
});
