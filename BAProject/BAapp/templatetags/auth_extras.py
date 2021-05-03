from django import template

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

@register.filter(name='has_no_group') 
def has_no_group(user, group_name):
    return not (user.groups.filter(name=group_name).exists()) 