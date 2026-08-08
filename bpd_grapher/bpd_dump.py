generate_variables(43)

VAR_PLAYER_OBJECT_0 = 0
VAR_OBJECT_1 = 1
VAR_PLAYER_NAMEDVARIABLE_2 = 2
VAR_FLOAT_3 = 3
VAR_FLOAT_4 = 4
VAR_FLOAT_5 = 5
VAR_FLOAT_6 = 6
VAR_PLAYER_NAMEDVARIABLE_7 = 7
VAR_ATTRIBUTE_8 = 8
VAR_ATTRIBUTE_9 = 9
VAR_ATTRIBUTE_10 = 10
VAR_BINARYMATH_11 = 11
VAR_FLOAT_12 = 12
VAR_PLAYER_NAMEDVARIABLE_13 = 13
VAR_UNARYMATH_14 = 14
VAR_VECTOR_15 = 15
VAR_DIRECTIONVECTOR_16 = 16
VAR_BINARYMATH_17 = 17
VAR_BINARYMATH_18 = 18
VAR_ATTRIBUTE_19 = 19
VAR_FLOAT_20 = 20
VAR_FLOAT_21 = 21
VAR_ATTRIBUTE_22 = 22
VAR_ATTRIBUTE_23 = 23
VAR_FLOAT_24 = 24
VAR_ATTRIBUTE_25 = 25
VAR_FLOAT_26 = 26
VAR_FLOAT_27 = 27
VAR_FLOAT_28 = 28
VAR_FLOAT_29 = 29
VAR_FLOAT_30 = 30
VAR_FLOAT_31 = 31
VAR_FLOAT_32 = 32
VAR_INSTANCEDATA_33 = 33
VAR_FLOAT_34 = 34
VAR_FLOAT_35 = 35
VAR_ATTRIBUTE_36 = 36
VAR_ATTRIBUTE_37 = 37
VAR_FLOAT_38 = 38
VAR_OBJECT_39 = 39
VAR_ATTRIBUTE_40 = 40
VAR_FLOAT_41 = 41
VAR_PLAYER_NAMEDVARIABLE_42 = 42


OnActivated_0 = EventData(event_name='OnActivated', output_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_42],'SkillInstigator',EBehaviorVariableLinkType.BVARLINK_Output,0)])
OnPaused_1 = EventData(event_name='OnPaused', output_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'SkillInstigator',EBehaviorVariableLinkType.BVARLINK_Output,0)])
DamagedAnEnemyWithMelee_2 = EventData(event_name='Damaged an Enemy with Melee', output_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'SkillInstigator',EBehaviorVariableLinkType.BVARLINK_Output,0), VariableLinkData([VAR_OBJECT_39],'Enemy',EBehaviorVariableLinkType.BVARLINK_Output,1)])
OnWeaponFired_3 = EventData(event_name='OnWeaponFired', output_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'SkillInstigator',EBehaviorVariableLinkType.BVARLINK_Output,0)])
OnDeactivated_4 = EventData(event_name='OnDeactivated', output_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'SkillInstigator',EBehaviorVariableLinkType.BVARLINK_Output,0)])
OnActionSkillActiveAbilityActivated_5 = EventData(event_name='OnActionSkillActiveAbilityActivated', output_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'SkillInstigator',EBehaviorVariableLinkType.BVARLINK_Output,0)])
OnActivated_6 = EventData(event_name='OnActivated', output_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'SkillInstigator',EBehaviorVariableLinkType.BVARLINK_Output,0)])


Behavior_DeactivateSkill_40_0 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_DeactivateSkill_40', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_DeactivateSkill_41_1 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_DeactivateSkill_41', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_ActivateSkill_48_2 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_ActivateSkill_48', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_AIPatsy_0_3 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_AIPatsy_0', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_2],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0), VariableLinkData([VAR_OBJECT_1],'Patsy',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_SimpleMath_32_4 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SimpleMath_32', linked_variables=[VariableLinkData([VAR_FLOAT_3],'A',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_4],'B',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_3],'Result',EBehaviorVariableLinkType.BVARLINK_Output,0)])
Behavior_ScreenParticle_12_5 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_ScreenParticle_12', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_CompareFloat_16_6 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_16', linked_variables=[VariableLinkData([VAR_FLOAT_5],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_6],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_DeactivateSkill_42_7 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_DeactivateSkill_42', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_CauseDamage_0_8 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CauseDamage_0', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_7],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0), VariableLinkData([VAR_OBJECT_1],'TargetContext',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_ATTRIBUTE_8],'DamageFormula',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_BINARYMATH_11],'StatusEffectDamage',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_CoordinatedEffect_20_9 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CoordinatedEffect_20', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_2],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_Explode_0_10 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_Explode_0', linked_variables=[VariableLinkData([VAR_OBJECT_1],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0), VariableLinkData([VAR_OBJECT_1],'DamageContext',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_ChangeCanTarget_0_11 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_ChangeCanTarget_0', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_SimpleMath_33_12 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SimpleMath_33', linked_variables=[VariableLinkData([VAR_FLOAT_5],'A',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_12],'B',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_5],'Result',EBehaviorVariableLinkType.BVARLINK_Output,0)])
Behavior_SpawnParticleSystem_0_13 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SpawnParticleSystem_0', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_13],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0), VariableLinkData([VAR_BINARYMATH_18],'RelativeLocation',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_CompareFloat_17_14 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_17', linked_variables=[VariableLinkData([VAR_ATTRIBUTE_19],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_20],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_DebugMessage_22_15 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_DebugMessage_22', linked_variables=[VariableLinkData([VAR_DIRECTIONVECTOR_16],'DebugVector',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_DebugMessage_23_16 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_DebugMessage_23')
Behavior_SimpleMath_34_17 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SimpleMath_34', linked_variables=[VariableLinkData([VAR_FLOAT_21],'A',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_ATTRIBUTE_22],'B',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_5],'Result',EBehaviorVariableLinkType.BVARLINK_Output,0)])
Behavior_CompareFloat_18_18 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_18', linked_variables=[VariableLinkData([VAR_ATTRIBUTE_23],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_24],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_SpawnParticleSystem_1_19 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SpawnParticleSystem_1', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_2],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_CompareFloat_19_20 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_19', linked_variables=[VariableLinkData([VAR_ATTRIBUTE_25],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_26],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_Delay_68_21 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_Delay_68', linked_variables=[VariableLinkData([VAR_FLOAT_27],'Delay',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_ChangeCanTarget_1_22 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_ChangeCanTarget_1', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_2],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_SimpleMath_35_23 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SimpleMath_35', linked_variables=[VariableLinkData([VAR_FLOAT_28],'A',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_29],'B',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_3],'Result',EBehaviorVariableLinkType.BVARLINK_Output,0)])
Behavior_Destroy_0_24 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_Destroy_0', linked_variables=[VariableLinkData([VAR_OBJECT_1],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_CompareFloat_20_25 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_20', linked_variables=[VariableLinkData([VAR_FLOAT_30],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_31],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_ScreenParticle_13_26 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_ScreenParticle_13', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_2],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_TriggerDialogEvent_45_27 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_TriggerDialogEvent_45', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0), VariableLinkData([VAR_OBJECT_1],'Other',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_CompareFloat_21_28 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_21', linked_variables=[VariableLinkData([VAR_ATTRIBUTE_22],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_32],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_Metronome_10_29 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_Metronome_10')
Behavior_SpawnProjectile_0_30 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SpawnProjectile_0', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0), VariableLinkData([VAR_INSTANCEDATA_33],'OwnerContext',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_ActivateSkill_49_31 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_ActivateSkill_49', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_2],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_SpawnParticleSystem_2_32 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SpawnParticleSystem_2', linked_variables=[VariableLinkData([VAR_OBJECT_1],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_CompareFloat_22_33 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_22', linked_variables=[VariableLinkData([VAR_FLOAT_3],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_29],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_CoordinatedEffect_21_34 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CoordinatedEffect_21', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_SimpleMath_36_35 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SimpleMath_36', linked_variables=[VariableLinkData([VAR_FLOAT_34],'A',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_35],'B',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_30],'Result',EBehaviorVariableLinkType.BVARLINK_Output,0)])
Behavior_SimpleMath_37_36 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SimpleMath_37', linked_variables=[VariableLinkData([VAR_ATTRIBUTE_36],'A',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_ATTRIBUTE_37],'B',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_ATTRIBUTE_36],'Result',EBehaviorVariableLinkType.BVARLINK_Output,0)])
Behavior_SimpleMath_38_37 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SimpleMath_38', linked_variables=[VariableLinkData([VAR_FLOAT_31],'A',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_38],'B',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_31],'Result',EBehaviorVariableLinkType.BVARLINK_Output,0)])
Behavior_DeactivateSkill_43_38 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_DeactivateSkill_43', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_CompareFloat_23_39 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_CompareFloat_23', linked_variables=[VariableLinkData([VAR_ATTRIBUTE_40],'ValueA',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_FLOAT_24],'ValueB',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_SpecialMove_23_40 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SpecialMove_23', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_Delay_69_41 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_Delay_69', linked_variables=[VariableLinkData([VAR_FLOAT_41],'Delay',EBehaviorVariableLinkType.BVARLINK_Input,0)])
Behavior_PostAkEvent_108_42 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_PostAkEvent_108', linked_variables=[VariableLinkData([VAR_PLAYER_OBJECT_0],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0)])
Behavior_SpawnFromPopulationSystem_0_43 = Behavior(behavior='GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0.Behavior_SpawnFromPopulationSystem_0', linked_variables=[VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_42],'Context',EBehaviorVariableLinkType.BVARLINK_Context,0), VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_42],'GameStageContext',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_PLAYER_NAMEDVARIABLE_42],'MyOwner',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_BINARYMATH_18],'SpawnLocOffset',EBehaviorVariableLinkType.BVARLINK_Input,0), VariableLinkData([VAR_OBJECT_1],'SpawnedActor',EBehaviorVariableLinkType.BVARLINK_Output,0)])


OnActivated_0 += BehaviorLink(Behavior_SpawnFromPopulationSystem_0_43)
Behavior_SpawnFromPopulationSystem_0_43 += BehaviorLink(Behavior_AIPatsy_0_3,-1)
Behavior_AIPatsy_0_3 += BehaviorLink(Behavior_ChangeCanTarget_1_22,-1)
Behavior_ChangeCanTarget_1_22 += BehaviorLink(Behavior_ActivateSkill_49_31,-1)
Behavior_ActivateSkill_49_31 += BehaviorLink(Behavior_SpawnParticleSystem_1_19,-1)
Behavior_SpawnParticleSystem_1_19 += BehaviorLink(Behavior_CoordinatedEffect_20_9,-1)
Behavior_CoordinatedEffect_20_9 += BehaviorLink(Behavior_ScreenParticle_13_26,-1)

OnPaused_1 += BehaviorLink(Behavior_SimpleMath_34_17)
Behavior_SimpleMath_34_17 += BehaviorLink(Behavior_CompareFloat_16_6,-1)
Behavior_CompareFloat_16_6 += BehaviorLink(Behavior_DeactivateSkill_43_38)
Behavior_CompareFloat_16_6 += BehaviorLink(Behavior_DeactivateSkill_43_38,1)
Behavior_CompareFloat_16_6 += BehaviorLink(Behavior_SimpleMath_33_12,2)
Behavior_SimpleMath_33_12 += BehaviorLink(Behavior_ActivateSkill_48_2,-1)
Behavior_ActivateSkill_48_2 += BehaviorLink(Behavior_CompareFloat_16_6,-1)

DamagedAnEnemyWithMelee_2 += BehaviorLink(Behavior_CompareFloat_23_39)
Behavior_CompareFloat_23_39 += BehaviorLink(Behavior_CompareFloat_18_18)
Behavior_CompareFloat_23_39 += BehaviorLink(Behavior_CompareFloat_18_18,1)
Behavior_CompareFloat_23_39 += BehaviorLink(Behavior_Delay_68_21,2)
Behavior_CompareFloat_18_18 += BehaviorLink(Behavior_Delay_68_21)
Behavior_CompareFloat_18_18 += BehaviorLink(Behavior_Delay_68_21,1)
Behavior_Delay_68_21 += BehaviorLink(Behavior_DeactivateSkill_41_1,-1)

OnWeaponFired_3 += BehaviorLink(Behavior_DeactivateSkill_42_7)

OnDeactivated_4 += BehaviorLink(Behavior_CompareFloat_17_14)
Behavior_CompareFloat_17_14 += BehaviorLink(Behavior_SpawnParticleSystem_2_32)
Behavior_CompareFloat_17_14 += BehaviorLink(Behavior_SpawnParticleSystem_2_32,1)
Behavior_CompareFloat_17_14 += BehaviorLink(Behavior_Explode_0_10,2)
Behavior_SpawnParticleSystem_2_32 += BehaviorLink(Behavior_TriggerDialogEvent_45_27,-1)
Behavior_TriggerDialogEvent_45_27 += BehaviorLink(Behavior_Destroy_0_24)
Behavior_Destroy_0_24 += BehaviorLink(Behavior_ChangeCanTarget_0_11,-1)
Behavior_ChangeCanTarget_0_11 += BehaviorLink(Behavior_CompareFloat_21_28,-1)
Behavior_CompareFloat_21_28 += BehaviorLink(Behavior_CoordinatedEffect_21_34)
Behavior_CompareFloat_21_28 += BehaviorLink(Behavior_CoordinatedEffect_21_34,1)
Behavior_CompareFloat_21_28 += BehaviorLink(Behavior_DeactivateSkill_40_0,2)
Behavior_CoordinatedEffect_21_34 += BehaviorLink(Behavior_ScreenParticle_12_5,-1)
Behavior_DeactivateSkill_40_0 += BehaviorLink(Behavior_CompareFloat_21_28,-1)
Behavior_Explode_0_10 += BehaviorLink(Behavior_CauseDamage_0_8,-1)
Behavior_CauseDamage_0_8 += BehaviorLink(Behavior_SpawnParticleSystem_2_32,-1)

OnActionSkillActiveAbilityActivated_5 += BehaviorLink(Behavior_CompareFloat_20_25)
Behavior_CompareFloat_20_25 += BehaviorLink(Behavior_CompareFloat_19_20,2)
Behavior_CompareFloat_19_20 += BehaviorLink(Behavior_SpecialMove_23_40,2)
Behavior_SpecialMove_23_40 += BehaviorLink(Behavior_PostAkEvent_108_42)
Behavior_PostAkEvent_108_42 += BehaviorLink(Behavior_SimpleMath_35_23)
Behavior_SimpleMath_35_23 += BehaviorLink(Behavior_CompareFloat_22_33,-1)
Behavior_CompareFloat_22_33 += BehaviorLink(Behavior_SimpleMath_38_37,1)
Behavior_CompareFloat_22_33 += BehaviorLink(Behavior_SpawnProjectile_0_30,2)
Behavior_SpawnProjectile_0_30 += BehaviorLink(Behavior_SimpleMath_32_4)
Behavior_SimpleMath_32_4 += BehaviorLink(Behavior_Delay_69_41,-1)
Behavior_Delay_69_41 += BehaviorLink(Behavior_CompareFloat_22_33,-1)

OnActivated_6 += BehaviorLink(Behavior_SimpleMath_36_35)


generate_bpd('GD_Assassin_Skills.ActionSkill.Skill_Stealth:BehaviorProviderDefinition_0')