" enable syntax highlighting
syntax enable
" show line numbers
set number
" set tabs to have 4 spaces
set ts=4
" indent when moving to the next line while writing code
set autoindent
" expand tabs into spaces
set expandtab
" when using the >> or << commands, shift lines by 4 spaces
set shiftwidth=4
" show a visual line under the cursor's current line
set cursorline
" show the matching part of the pair for [] {} and ()
set showmatch
" enable all Python syntax highlighting features
let python_highlight_all = 1
" I addedd newly
execute pathogen#infect()
syntax on
filetype plugin indent on
"Autocomplete for JS, CSS and HTML
autocmd FileType html set omnifunc=htmlcomplete#CompleteTags
autocmd FileType javascript set omnifunc=javascriptcomplete#CompleteJS
autocmd FileType css set omnifunc=csscomplete#CompleteCSS
let g:user_emmet_settings = { 'php' : { 'extends' : 'html', 'filters' : 'c', }, 'xml' : { 'extends' : 'html', }, 'haml' : { 'extends' : 'html', }, }
