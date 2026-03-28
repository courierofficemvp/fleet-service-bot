# вставь только этот кусок в файл вместо accept

@router.callback_query(F.data.startswith("accept:"))
async def accept(cb: CallbackQuery):
    service_id = cb.data.split(":")[1]

    service = get_by_id(service_id)

    if not service:
        await cb.answer("❌ Сервис не найден", show_alert=True)
        return

    # 🔥 если уже кто-то взял
    if service.get("status") != "pending":
        await cb.answer("❌ Уже взят другим механиком", show_alert=True)
        return

    user_display = get_user_display(cb.from_user)

    update_status(service_id, "in_progress", user_display)

    await cb.message.answer(
        f"✅ Ты взял этот сервис\n👨‍🔧 {user_display}",
        reply_markup=complete_kb(service_id)
    )

    await cb.answer()
