<template>
  <div class="relative">
    <TextInput
      v-model="searchQuery"
      type="search"
      placeholder="Search records..."
      class="w-full"
      @input="handleSearch"
    />
    
    <div
      v-if="results.length > 0"
      class="absolute w-full mt-2 bg-white shadow-lg rounded-md max-h-96 overflow-y-auto border"
    >
      <div
        v-for="result in results"
        :key="result.name"
        class="p-3 hover:bg-gray-100 cursor-pointer border-b"
        @click="handleResultClick(result)"
      >
        <div class="font-medium">{{ result.title }}</div>
        <div class="text-sm text-gray-600 line-clamp-2">
          {{ stripHtml(result.description) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { TextInput } from 'frappe-ui';
import { frappe } from 'frappe-ui';

const searchQuery = ref('');
const results = ref([]);
let debounceTimer = null;

const stripHtml = (html) => {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
};

const handleSearch = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    if (searchQuery.value.length >= 3) {
      try {
        const { data } = await frappe.get('your_app.api.search_records', {
          params: { text: searchQuery.value }
        });
        results.value = data.message;
      } catch (error) {
        console.error('Search failed:', error);
      }
    }
  }, 300);
};

const handleResultClick = (result) => {
  // Handle navigation or selection
  console.log('Selected:', result);
  results.value = [];
  searchQuery.value = '';
};
</script>