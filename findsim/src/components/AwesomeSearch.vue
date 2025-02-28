<template>
  <div class="relative">
    <div class="flex">
      <TextInput
        v-model="searchQuery"
        type="search"
        placeholder="Search records..."
        class="w-full p-2"
        @input="handleSearch"
      />
      <TextInput
        v-model="searchQueryAI"
        type="search"
        placeholder="AI Search..."
        class="w-full p-2"
        @change="handleSearchAI"
      />
    </div>

    <div 
      v-if="searchQuery || searchQueryAI"
      class="absolute w-full mt-2 flex gap-4"
    >
      <!-- Regular Results Column -->
      <div 
        class="flex-1 bg-white shadow-lg rounded-md max-h-96 overflow-y-auto border"
        :class="{ 'opacity-50': searchResource.loading }"
      >
        <div v-if="searchQuery">
          <div v-if="searchResource.loading" class="p-3 text-gray-500">
            Searching regular results...
          </div>
          <div v-else>
            <div
              v-for="result in results"
              :key="result.name"
              class="p-3 hover:bg-gray-100 cursor-pointer border-b"
              @click="handleResultClick(result)"
            >
              <div class="font-medium" dir="rtl" v-html="highlightText(result.description)"></div>
              <div class="text-sm text-gray-600 line-clamp-2" dir="rtl">
                {{ stripHtml(result.description) }}
              </div>
            </div>
            <div v-if="!searchResource.loading && results.length === 0" class="p-3 text-gray-500">
              No regular results found
            </div>
          </div>
        </div>
      </div>

      <!-- AI Results Column -->
      <div 
        class="flex-1 bg-white shadow-lg rounded-md max-h-96 overflow-y-auto border"
        :class="{ 'opacity-50': aiSearchLoading }"
      >
        <div v-if="searchQueryAI">
          <div v-if="aiSearchLoading" class="p-3 text-gray-500">
            Analyzing with AI...
          </div>
          <div v-else>
            <div
              v-for="result in resultsAI"
              :key="result.index"
              class="p-3 hover:bg-gray-100 cursor-pointer border-b"
            >
              <div class="flex justify-between">
                <div class="font-medium" dir="rtl">{{ result.Description }}</div>
                <div class="text-blue-600 font-semibold">
                  {{ (result.similarity_score * 100).toFixed(2) }}%
                </div>
              </div>
            </div>
            <div v-if="!aiSearchLoading && resultsAI.length === 0" class="p-3 text-gray-500">
              No AI results found
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { TextInput } from 'frappe-ui';
import { createResource } from 'frappe-ui';

const searchQuery = ref('');
const searchQueryAI = ref('');
const results = ref([]);
const resultsAI = ref([]);
let debounceTimer = null;


// Watch for any change in searchQueryAI
// watch(searchQueryAI, (newValue, oldValue) => {
//   handleSearchAI(newValue, oldValue);
// });

// Create search resource
const searchResource = createResource({
  url: 'find_sim.api.search_description',
  method: 'GET',
  auto: false,

  
  validate(params) {
    console.log('Search query 2 :', params);
    return params.query?.length >= 3;
  },
  onSuccess(data) {
    
   results.value = data || [];
   console.log('Search data.message:', data);
   console.log('Search results.value:', results.value);
  },
  onError(error) {
    console.error('Search failed:', error);
    results.value = [];
  }
});

// search for similarities
const searchResourceAI = createResource({
  url: 'find_sim.api.similar_description',
  method: 'GET',
  auto: false,

  validate(params) {
    console.log('Search query 2 :', params);
    return params.query?.length >= 3;
  },
  onSuccess(data) {
    
   resultsAI.value = data || [];
   console.log('Search AI results.value:', resultsAI.value);
  },
  onError(error) {
    console.error('Search AI failed:',error);
    resultsAI.value = [];
  }
});

const stripHtml = (html) => {
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
};

const highlightText = (text) => {
  // If there's no search or no text, just return the original text
  if (!searchQuery.value || !text) return text;

  // Split the search query by spaces => subqueries
  // e.g. ["apple", "banana"]
  // Then also add the entire query => ["apple", "banana", "apple banana"]
  let tokens = searchQuery.value.trim().split(/\s+/).filter(Boolean);
  tokens.push(searchQuery.value.trim());

  // Sort tokens from longest to shortest so
  // the entire query is matched first if present
  tokens.sort((a, b) => b.length - a.length);

  // Build a single OR pattern: (apple banana|apple|banana)
  const pattern = tokens.map(escapeRegex).join('|');
  const regex = new RegExp(pattern, 'gi');

  // Replace each match with a highlighted span
  return text.replace(regex, (match) => {
    return `<span class="bg-yellow-300">${match}</span>`;
  });
};

// Utility to escape special regex characters
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

const highlightText1 = (text) => {
  const query = searchQuery.value.toLowerCase();
  //if (!query) return text;
  
  return text.replace(
    new RegExp(query, 'i'),
    match => `<span class="bg-yellow-300">${match}</span>`
  );
};

const handleSearch = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (searchQuery.value.length >= 3) {
      console.log('Search query length>=3 :', searchQuery.value);
      searchResource.fetch({
        query: searchQuery.value 
        
      });
    } else {
      results.value = [];
    }
  }, 300);
};

const handleSearchAI = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    if (searchQueryAI.value.length >= 3) {
      console.log('Search query length>=3 :', searchQueryAI.value);
      searchResourceAI.fetch({
        query: searchQueryAI.value 
        
      });
    } else {
      results.value = [];
    }
  }, 300);
};

const handleResultClick = (result) => {
  // Handle navigation or selection
  console.log('Selected:', result);
  //results.value = [];
  //searchQuery.value = '';
  resultsAI.value = [];
  searchQueryAI.value = result.description;
  handleSearchAI();
};

// Keyboard navigation
const selectedIndex = ref(-1);

watch(searchQuery, () => {
  selectedIndex.value = -1;
});

const handleKeydown = (e) => {
  if (e.key === 'ArrowDown') {
    selectedIndex.value = Math.min(selectedIndex.value + 1, results.value.length - 1);
  } else if (e.key === 'ArrowUp') {
    selectedIndex.value = Math.max(selectedIndex.value - 1, -1);
  } else if (e.key === 'Enter' && selectedIndex.value >= 0) {
    handleResultClick(results.value[selectedIndex.value]);
  }
};
</script>

<style>
.bg-yellow-100 {
  background-color: #fef9c3;
}
</style>