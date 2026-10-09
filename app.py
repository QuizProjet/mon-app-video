                                elapsed=reflection_duration*j/steps
                                if elapsed<1.05:
                                    sec=3
                                    frac=1-(elapsed/1.05)
                                elif elapsed<2.10:
                                    sec=2
                                    frac=1-((elapsed-1.05)/1.05)
                                elif elapsed<3.15:
                                    sec=1
                                    frac=1-((elapsed-2.10)/1.05)
                                else:
                                    sec=None
                                    frac=0.0

                                cframes.append((
                                    draw_vocab_cumulative_frame(
                                        items,idx,theme_v,channel_v,bg_v,
                                        timer=sec,
                                        timer_fraction=max(0.0,frac),
                                        reveal=False,
                                        motion=elapsed/reflection_duration,
                                        video_title=th_v,
                                        # Le mot français reste visible pendant 3-2-1.
                                        source_active_word=fr_last_word
                                    ),
                                    reflection_duration/steps
                                ))

                            count_clip=os.path.join(tmp,f"count_{idx}.mp4")
                            make_vocab_style2_segment(
                                save_frames(cframes,tmp,f"vc_{idx}"),
                                countdown_sfx,count_clip,tmp,1.0
                            )

                            # --- 3. TRADUCTION + VOIX, puis conservation de la ligne ---
                            ta=os.path.join(tmp,f"tr_{idx}.mp3")
                            tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate)
                            td=audio_duration(ta)

                            tf=word_timed_frames_vocab_style2(
                                ta,tw,
                                lambda wi,prog: draw_vocab_cumulative_frame(
                                    items,idx,theme_v,channel_v,bg_v,
                                    reveal=True,motion=prog,
                                    video_title=th_v,
                                    # Le français reste définitivement visible
                                    # pendant que la traduction est prononcée.
                                    source_active_word=fr_last_word,
                                    translation_active_word=wi
                                ),
                                td
                            )

                            tr_fx=os.path.join(tmp,f"tr_fx_{idx}.m4a")
                            if sfx_cfg.get("sfx_enabled",True):
                                mix_voice_sfx(
                                    ta,pop,tr_fx,0,
                                    float(sfx_cfg.get("sfx_volume",0.30))
                                )
                            else:
                                tr_fx=ta

                            tr_clip=os.path.join(tmp,f"tr_{idx}.mp4")
                            make_vocab_style2_segment(
                                save_frames(tf,tmp,f"trf_{idx}"),
                                tr_fx,tr_clip,tmp,1.0
                            )

                            # On regroupe immédiatement les 3 phases du mot.
                            # Cela empêche les petits écarts de timebase de se
                            # cumuler sur 15 mots.
                            item_clip=os.path.join(tmp,f"item_{idx}.mp4")
                            concat_videos_style2(
                                [fr_clip,count_clip,tr_clip],
                                item_clip,tmp
                            )
                            clips.append(item_clip)

                        else:
                            fwords=word_timed_frames(fa,fw,lambda wi,prog: draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"mot",entrance=prog,source_active_word=wi),fd)
                            word_voice_fx=os.path.join(tmp,f"fr_fx_{idx}.m4a")
                            sfx_cfg=_layout("vocab","1")
                            if sfx_cfg.get("sfx_enabled",True): mix_voice_sfx(fa,pop,word_voice_fx,0,float(sfx_cfg.get("sfx_volume",0.30)))
                            else: word_voice_fx=fa
                            fo=os.path.join(tmp,f"fr_{idx}.mp4"); make_segment(save_frames(fwords,tmp,f"vf_{idx}"),word_voice_fx,fo,tmp); clips.append(fo)
                            cframes=[]
                            for j in range(COUNTDOWN_STEPS):
                                t=j/max(1,31); elapsed=t*3.12
                                if elapsed<1.02: sec=3; frac=1-(elapsed/1.02)
                                elif elapsed<2.04: sec=2; frac=1-((elapsed-1.02)/1.02)
                                elif elapsed<3.0: sec=1; frac=1-((elapsed-2.04)/.96)
                                else: sec=None; frac=0.0
                                cframes.append((draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"countdown",sec,frac,1.0),3.12/32))
                            co=os.path.join(tmp,f"count_{idx}.mp4"); make_segment(save_frames(cframes,tmp,f"vc_{idx}"),countdown_sfx,co,tmp,.92); clips.append(co)
                            ta=os.path.join(tmp,f"tr_{idx}.mp3"); tw=synthesize_audio(item['trad'],voice_tr,ta,tts_rate); td=audio_duration(ta)
                            tf=word_timed_frames(ta,tw,lambda wi,prog: draw_vocab_frame(items,idx,langue_v,theme_v,channel_v,bg_v,"translation",entrance=1.0,translation_active_word=wi),td)
                            tr_fx=os.path.join(tmp,f"tr_fx_{idx}.m4a")
                            if sfx_cfg.get("sfx_enabled",True): mix_voice_sfx(ta,pop,tr_fx,0,float(sfx_cfg.get("sfx_volume",0.30)))
                            else: tr_fx=ta
                            tro=os.path.join(tmp,f"tr_{idx}.mp4"); make_segment(save_frames(tf,tmp,f"trf_{idx}"),tr_fx,tro,tmp); clips.append(tro)
                        gc.collect()
                    oa=os.path.join(tmp,"vo.mp3"); synthesize_audio(outro_v,VOICES_FR["Henri - Dynamique"],oa,tts_rate); od=audio_duration(oa)
                    if style_v.startswith("Style 2"):
                        of=save_frames([(draw_page_template(outro_v+((" "+outro_v_sub) if clean_text(outro_v_sub) else ""),theme_v,channel_v,bg_v,p,"outro",st.session_state.get(("v2_" if style_v.startswith("Style 2") else "v1_")+"outro_page_variant","Premium lumineux"),"vocab","2" if style_v.startswith("Style 2") else "1",langue_v),max(.04,od/7)) for p in [.08,.28,.50,.72,.90,1.0]],tmp,"vo")
                    else:
                        of=save_frames([(draw_page_template(outro_v,theme_v,channel_v,bg_v,p,"outro",st.session_state.get("v1_outro_page_variant","Premium lumineux"),"vocab","1",langue_v),max(.04,od/7)) for p in [.08,.28,.50,.72,.90,1.0]],tmp,"vo")
                    oo=os.path.join(tmp,"vo.mp4"); make_segment(of,oa,oo,tmp); clips.append(oo)
                    final=os.path.join(tmp,"vocabulaire_pro.mp4")
                    if style_v.startswith("Style 2"):
                        concat_videos_style2(clips,final,tmp)
                    else:
                        concat_videos(clips,final,tmp)
                    with open(final,"rb") as f: data=f.read()
                    st.session_state["last_vocab_video_data"] = data
                    st.success("✅ Short Vocabulaire Pro terminé.")
                    st.video(data)
                    st.download_button("⬇️ Télécharger vocabulaire_pro.mp4",data=data,file_name="vocabulaire_pro.mp4",mime="video/mp4",key="dv4")
        except MemoryError:
            gc.collect(); st.error("La mémoire a été saturée pendant le rendu. Relance l'application puis réessaie.")
        except Exception as e: st.error(f"Erreur pendant le montage : {e}")

# Export persistant : placé après le rendu pour rester disponible après chaque rerun Streamlit.
if st.session_state.get("last_quiz_video_data"):
    render_export_panel(st.session_state["last_quiz_video_data"],"SuspenseLingo_Quiz","export_quiz_persist")
if st.session_state.get("last_vocab_video_data"):
    render_export_panel(st.session_state["last_vocab_video_data"],"SuspenseLingo_Vocabulaire","export_vocab_persist")

st.markdown('</div>',unsafe_allow_html=True)
