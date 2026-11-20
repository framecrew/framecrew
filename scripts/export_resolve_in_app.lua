function FrameCrewExport(app, name, media_path, archive_path)
    assert(bmd.fileexists(media_path), "Media file missing: " .. media_path)
    assert(not bmd.fileexists(archive_path), "Export already exists: " .. archive_path)

    local manager = assert(app:GetProjectManager(), "Resolve project manager unavailable")
    local project = assert(manager:CreateProject(name), "Could not create project: " .. name)
    local pool = assert(project:GetMediaPool(), "Media pool unavailable")
    local root = assert(pool:GetRootFolder(), "Root bin unavailable")
    assert(pool:AddSubFolder(root, "Raw Footage"), "Could not create Raw Footage bin")
    assert(pool:AddSubFolder(root, "Proxy"), "Could not create Proxy bin")
    local output = assert(pool:AddSubFolder(root, "Output"), "Could not create Output bin")
    assert(pool:SetCurrentFolder(output), "Could not select Output bin")

    local clips = pool:ImportMedia({ media_path })
    assert(clips and clips[1], "Could not import media: " .. media_path)
    local timeline = assert(pool:CreateTimelineFromClips(name .. "_Master", { clips[1] }),
        "Could not create timeline")
    local video = timeline:GetItemListInTrack("video", 1)
    local audio = timeline:GetItemListInTrack("audio", 1)
    assert(video and #video > 0, "Imported timeline has no video")
    assert(audio and #audio > 0, "Imported timeline has no audio")
    assert(manager:SaveProject(), "Could not save project")
    assert(manager:ExportProject(name, archive_path), "Could not export project")
    assert(bmd.fileexists(archive_path), "Project archive missing")
    return archive_path
end
