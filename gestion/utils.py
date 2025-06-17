def get_queryset_by_role(model, user):
    if user.is_superuser:
        return model.objects.none()  # l’admin ne voit rien ici

    if user.role == 'superviseur':
        return model.objects.all()

    return model.objects.filter(agent=user)