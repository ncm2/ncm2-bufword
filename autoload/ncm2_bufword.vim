if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

let g:ncm2_bufword#proc = yarp#py3({
    \ 'module': 'ncm2_bufword',
    \ 'on_load': { -> ncm2#set_ready(g:ncm2_bufword#source)}
    \ })

let g:ncm2_bufword#source = extend(get(g:, 'ncm2_bufword#source', {}), {
            \ 'name': 'bufword',
            \ 'ready': 0,
            \ 'priority': 5,
            \ 'mark': 'b',
            \ 'on_complete': 'ncm2_bufword#on_complete',
            \ 'on_warmup': 'ncm2_bufword#on_warmup',
            \ }, 'keep')

func! ncm2_bufword#init()
    call ncm2#register_source(g:ncm2_bufword#source)
endfunc

func! ncm2_bufword#on_warmup(ctx)
    call g:ncm2_bufword#proc.jobstart()
endfunc

func! ncm2_bufword#on_complete(ctx)
    call g:ncm2_bufword#proc.try_notify('on_complete', a:ctx)
endfunc

