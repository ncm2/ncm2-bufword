if get(s:, 'loaded', 0)
    finish
endif
let s:loaded = 1

let g:ncm2_bufword#proc = yarp#py3('ncm2_bufword')

let g:ncm2_bufword#source = get(g:, 'ncm2_bufword#source', {
            \ 'name': 'bufword',
            \ 'priority': 5,
            \ 'mark': 'b',
            \ 'on_complete': 'ncm2_bufword#on_complete',
            \ 'on_warmup': 'ncm2_bufword#on_warmup',
            \ })

let g:ncm2_bufword#source = extend(g:ncm2_bufword#source,
            \ get(g:, 'ncm2_bufword#source_override', {}),
            \ 'force')

func! ncm2_bufword#init()
    call ncm2#register_source(g:ncm2_bufword#source)
endfunc

func! ncm2_bufword#on_warmup(ctx)
    call g:ncm2_bufword#proc.jobstart()
endfunc

func! ncm2_bufword#on_complete(ctx)
    call g:ncm2_bufword#proc.try_notify('on_complete', a:ctx)
endfunc

