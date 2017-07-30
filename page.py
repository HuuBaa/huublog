#!/usr/bin/env python3
# -*- coding: utf-8 -*-
def getPageStr(page_str):
    p=1
    try:
        p=int(page_str)
    except ValueError as e:
        pass
    if p<1:
        p=1
    return p

class Page(object):
    def __init__(self,item_count,page_index=1,page_size=10):
        self.item_count=item_count
        self.page_size=page_size
        self.page_count=item_count // page_size + (1 if item_count % page_size > 0 else 0)
        if (item_count==0) or (page_index>self.page_count):
            self.page_index=1
            self.offset=0
            self.limit=0
        else:
            self.page_index=page_index
            self.offset=self.page_size*(page_index-1)
            self.limit=self.page_size
            
        self.has_next=self.page_index < self.page_count
        self.has_prev=self.page_index > 1