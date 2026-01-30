import { useState } from "react";
import { profileEditSchema, ProfileEditInput } from "../types";
import { usersApi } from "@/lib/api/users";
import { uploadsApi } from "@/lib/api/uploads";
import { UserProfile } from "@/types/api";

export function useProfileEdit(initial: ProfileEditInput) {
  const [form, setForm] = useState<ProfileEditInput>(initial);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const validate = () => {
    const result = profileEditSchema.safeParse(form);
    if (!result.success) {
      setError(result.error.errors[0]?.message ?? "入力内容を確認してください");
      return false;
    }
    setError(null);
    return true;
  };

  const handleChange = (field: keyof ProfileEditInput, value: any) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (): Promise<UserProfile | null> => {
    if (!validate()) return null;
    setSaving(true);
    try {
      let avatar_asset_id: string | undefined = undefined;
      if (form.avatar) {
        const asset = await uploadsApi.uploadImage(form.avatar, "avatar");
        avatar_asset_id = asset.id;
      }
      const updatedUser = await usersApi.updateProfile({
        first_name: form.first_name,
        last_name: form.last_name,
        bio: form.bio,
        ...(avatar_asset_id ? { avatar_asset_id } : {}),
      });
      setSaving(false);
      return updatedUser;
    } catch (e: any) {
      setError(e?.message ?? "更新に失敗しました");
      setSaving(false);
      return null;
    }
  };

  return {
    form,
    error,
    saving,
    setForm,
    handleChange,
    handleSubmit,
  };
}
